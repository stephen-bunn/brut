# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

import json
from datetime import datetime
from functools import lru_cache
from typing import Generator

from cached_property import cached_property
from praw import Reddit
from praw.models import Submission, Subreddit

from ..db import Content
from ..env import instance as env
from ..log import instance as log
from .base import BaseIntegration

SOURCE = "reddit"


class SubredditIntegration(BaseIntegration):

    name: str = "subreddit"

    @cached_property
    def reddit(self) -> Reddit:
        log.info(
            f"Building read-only Reddit instance using client {env.reddit.client_id!r}"
        )
        reddit = Reddit(
            client_id=env.reddit.client_id,
            client_secret=env.reddit.client_secret,
            user_agent=env.reddit.user_agent,
        )
        reddit.read_only = True
        return reddit

    @lru_cache
    def get_subreddit(self, subreddit: str) -> Subreddit:
        log.debug(f"Fetching subreddit instance for subreddit {subreddit!r}")
        return self.reddit.subreddit(subreddit)

    def iter_subreddit(self, subreddit: str) -> Generator[Submission, None, None]:
        log.debug(f"Iterating over new submissions from subreddit {subreddit!r}")
        return self.get_subreddit(subreddit).new()

    def iter_content(  # type: ignore
        self, subreddit: str
    ) -> Generator[Content, None, None]:
        for submission in self.iter_subreddit(subreddit):
            log.debug(
                f"Building content entry for submission {submission.id!r} "
                f"from subreddit {subreddit!r}"
            )

            yield Content(
                created_at=datetime.fromtimestamp(submission.created_utc),
                source=SOURCE,
                source_id=submission.id,
                fingerprint=self.get_fingerprint(SOURCE, submission.id),
                url=submission.url,
                data=json.dumps(
                    {
                        "id": submission.id,
                        "is_self": submission.is_self,
                        "name": submission.name,
                        "title": submission.title,
                        "created_utc": submission.created_utc,
                        "permalink": submission.permalink,
                    }
                ),
            )
