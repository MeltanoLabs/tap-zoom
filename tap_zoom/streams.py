"""Stream type classes for tap-zoom."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from singer_sdk._singerlib import Schema
from singer_sdk.plugin_base import PluginBase as TapBaseClass

from tap_zoom.client import ZoomStream
from typing import Iterable, Any
import datetime
from dateutil.relativedelta import relativedelta

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class UsersStream(ZoomStream):
    """List users stream."""

    # https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/users
    # Scopes: user:read:admin
    # rate limit: Medium
    # max page size:  page_size = 300

    name = "users"
    path = "/users"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.users[*]"
    schema_filepath = SCHEMAS_DIR / "users.json"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "user_id": record["id"],
        }

class MeetingsStream(ZoomStream):
    """List meetings stream."""

    # https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetings
    # Scopes: meeting:read,meeting:read:admin
    # rate limit: Medium
    # max page size:  page_size = 300

    name = "meetings"
    parent_stream_type = UsersStream
    path = "/users/{user_id}/meetings"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.meetings[*]"
    schema_filepath = SCHEMAS_DIR / "meetings.json"

class RecordingsStream(ZoomStream):
    """List recording stream."""

    # https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/recordingsList
    # Scopes: recording:read:admin,recording:read
    # rate limit: Medium
    # max page size:  page_size = 300

    name = "recordings"
    parent_stream_type = UsersStream
    path = "/users/{user_id}/recordings"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.meetings[*]"
    schema_filepath = SCHEMAS_DIR / "recordings.json"

    def __init__(self, *args, **kwargs):
        """Initialize the REST stream.

        Args:
            tap: Singer Tap this stream belongs to.
            schema: JSON schema for records in this stream.
            name: Name of this stream.
            path: URL path for this entity stream.
        """
        super().__init__(*args, **kwargs)
        self._from_date = None
        self._to_date = None

    def _get_month_ranges(self, start_date: datetime.datetime) -> list[tuple[datetime.datetime, datetime.datetime]]:
        """
        Generates a list of tuples representing 1-month ranges from a past date until today.

        Args:
            start_date: A datetime object representing a date in the past.

        Returns:
            A list of tuples, where each tuple represents a 1-month range (start date, end date).
        """
        current_date = start_date
        month_ranges = []
        today = datetime.date.today()
        while current_date <= today:
            next_month = current_date + relativedelta(months=1)
            last_day_of_month = next_month - datetime.timedelta(days=1)
            month_ranges.append((current_date, last_day_of_month))
            current_date = next_month
        return month_ranges

    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Return a generator of record-type dictionary objects.

        Each record emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """
        # 1 month range max so we need to chunk up into months or separate queries
        # TODO: use SDK method for coalescing start_date and bookmark
        start_date = self.config.get("start_date")
       
        month_ago = (datetime.date.today() - datetime.timedelta(days=30))
        if start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            if start_date < month_ago:
                ranges = self._get_month_ranges(start_date)
                for (start, end) in ranges:
                    self._from_date = start
                    self._to_date = end
                    # set an object var that get_url_params uses if thats called after this
                    yield from super().get_records(context)
        else:
            yield from super().get_records(context)

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        base_parms = super().get_url_params(context, next_page_token)
        # Override date range since its a max of 1 month per iteration
        if self._from_date and self._to_date:
            base_parms["from"] = self._from_date
            base_parms["to"] = self._to_date
        return base_parms
