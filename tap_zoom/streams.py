"""Stream type classes for tap-zoom."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from tap_zoom.client import ZoomStream

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
    schema_filepath = SCHEMAS_DIR / "recordings.json"
