# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains Reddit.com based watchers."""

import json
from datetime import datetime
from functools import lru_cache
from typing import Generator

from cached_property import cached_property
from praw import Reddit
from praw.models import Submission, Subreddit

from ..config import instance as config
from ..db import Content
from ..log import instance as log
from .base import BaseWatcher

SOURCE = "reddit"


class SubredditWatcher(BaseWatcher):
    """The Reddit subreddit watcher.

    Watches for new content from a given Reddit subreddit.
    """

    type: str = "subreddit"

    @cached_property
    def reddit(self) -> Reddit:
        """Read-only Reddit connection client.

        Returns:
            ~praw.Reddit: The PRAW Reddit instance.
        """

        log.info(
            "Building read-only Reddit instance using client "
            f"{config.watchers.reddit.client_id!r}"
        )
        reddit = Reddit(
            client_id=config.watchers.reddit.client_id,
            client_secret=config.watchers.reddit.client_secret,
            user_agent=config.watchers.reddit.user_agent,
        )
        reddit.read_only = True
        return reddit

    @lru_cache
    def get_subreddit(self, subreddit: str) -> Subreddit:
        """Get a specific subreddit instance.

        Args:
            subreddit (str): The name of the subreddit to fetch.

        Returns:
            ~praw.models.Subreddit: The PRAW Subreddit instance.
        """

        log.debug(f"Fetching subreddit instance for subreddit {subreddit!r}")
        return self.reddit.subreddit(subreddit)

    def iter_subreddit(self, subreddit: str) -> Generator[Submission, None, None]:
        """Iterate over submissions from a given subreddit.

        Args:
            subreddit (str):
                The subreddit to iterate submissions.

        Yields:
            ~praw.models.Submission:
                A submission from the fetched subreddit.
        """

        log.debug(f"Iterating over new submissions from subreddit {subreddit!r}")
        return self.get_subreddit(subreddit).new()

    def iter_content(  # type: ignore
        self, subreddit: str
    ) -> Generator[Content, None, None]:
        """Iterate over a given subreddit submissions to produce content entries.

        Args:
            subreddit (str):
                The subreddit to iterate over new content.

        Yields:
            ~brut.db.Content:
                The extracted content from the subreddit.
        """

        for submission in self.iter_subreddit(subreddit):
            log.debug(
                f"Building content entry for submission {submission.id!r} "
                f"from subreddit {subreddit!r}"
            )

            yield Content(
                created_at=datetime.fromtimestamp(submission.created_utc),
                source=SOURCE,
                source_id=submission.id,
                fingerprint=Content.build_fingerprint(SOURCE, submission.id),
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
