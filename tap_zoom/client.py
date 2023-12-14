"""REST client handling, including ZoomStream base class."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl

from memoization import cached
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

from tap_zoom.auth import ZoomOAuthAuthenticator
from tap_zoom.pagination import ZoomPaginator

DEFAULT_URL = "https://api.zoom.us/v2"


class ZoomStream(RESTStream):
    """Zoom stream class."""

    next_page_token_jsonpath = "$.next_page_token"

    @property
    def url_base(self) -> str:
        return self.config.get("api_url", DEFAULT_URL)

    @property
    @cached  # type: ignore
    def authenticator(self) -> ZoomOAuthAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return ZoomOAuthAuthenticator(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")

        headers["Accept"] = "application/json"
        return headers

    def get_new_paginator(self) -> BaseAPIPaginator:
        # return JSONPathPaginator(self.next_page_token_jsonpath)
        return ZoomPaginator(self.next_page_token_jsonpath)

    def _get_stream_config(self) -> dict:
        """Get parameters set in config."""
        config: dict = {}

        stream_configs = self.config.get("stream_config", [])
        if not stream_configs:
            return config

        config_list = [
            conf for conf in stream_configs if conf.get("stream") == self.name
        ] or [None]
        config_dict = config_list[-1] or {}
        stream_config = {k: v for k, v in config_dict.items() if k != "stream"}
        return stream_config

    def _get_stream_params(self) -> dict:
        stream_params = self._get_stream_config().get("parameters", "")
        return {qry[0]: qry[1] for qry in parse_qsl(stream_params.lstrip("?"))}

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}

        # Tap Params
        page_size = self.config.get("page_size")
        if page_size:
            params["page_size"] = page_size

        if self.config.get("start_date"):
            params["from"] = self.config.get("start_date")

        # Stream Params
        stream_params = self._get_stream_params()
        params = {**params, **stream_params}

        # Pagination Params
        if next_page_token:
            if isinstance(next_page_token, dict):
                return {**params, **next_page_token}

            params["next_page_token"] = next_page_token

        return params
