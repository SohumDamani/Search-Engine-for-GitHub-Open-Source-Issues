import os
import time
from typing import Any, Dict, List, Optional

import requests

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """
    Small helper around the GitHub REST API.

    Goals:
    - Centralize auth (read token from env).
    - Handle pagination (GitHub returns results in pages).
    - Handle basic rate limiting (sleep and retry if we hit the limit).
    """

    def __init__(self, token: Optional[str] = None) -> None:
        # Prefer an explicit token, else read from GITHUB_TOKEN env var.
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is missing. Set token in .env file or pass as an argument to the class")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            # Identifies our project to GitHub (good practice).
            "User-Agent": "cs242-devdiscover-project"
        })

    def _request(self, method: str, path: str,
                 params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Low-level HTTP helper.

        - Builds the full URL from a path (e.g. '/search/repositories').
        - Handles 403 rate-limit responses by sleeping and retrying.
        - Raises for other HTTP errors.
        """
        url = f"{GITHUB_API_BASE}{path}"
        while True:
            resp = self.session.request(method, url, params=params)
            # If we hit the rate limit, GitHub returns 403 with specific headers.
            if resp.status_code == 403 and "rate limit" in resp.text.lower():
                reset_ts = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
                sleep_secs = max(reset_ts - time.time(), 30)
                print(f"Rate limited. Sleeping for {int(sleep_secs)} seconds...")
                time.sleep(sleep_secs)
                continue

            # Issues other than rate limit errors are raised here.
            resp.raise_for_status()
            return resp

    def get_json(self, path: str,
                 params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Convenience wrapper: perform a GET and return JSON-decoded body.
        """
        resp = self._request("GET", path, params=params)
        return resp.json()

    def get_paginated(self, path: str,
                      params: Optional[Dict[str, Any]] = None,
                      per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all pages of a paginated endpoint that returns a JSON list per page.
        We will use this later for endpoints like listing issues for a repo.
        """
        params = dict(params or {})
        params["per_page"] = per_page

        page = 1
        results: List[Dict[str, Any]] = []

        while True:
            params["page"] = page
            data = self.get_json(path, params=params)

            if not isinstance(data, list) or not data:
                break

            results.extend(data)

            if len(data) < per_page:
                # Last page
                break

            page += 1

        return results
