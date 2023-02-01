"""Defines a watcher for Reddit."""

from functools import cached_property
from typing import Iterator

from praw import Reddit
from praw.models import Submission, Subreddit

from brut.db import client
from brut.db.models import Artifact
from brut.env import instance as env
from brut.log import get_logger
from brut.types import WatcherProtocol

log = get_logger()


class RedditWatcher(WatcherProtocol):
    """The Reddit watcher to fetch Reddit URLs."""

    type = "reddit"
    """The type of the Reddit watcher."""

    @cached_property
    def reddit(self) -> Reddit:
        """The Reddit client instance for the watcher."""

        log.debug(f"Building read-only Reddit client using id {env.reddit.client_id}")
        reddit = Reddit(
            client_id=env.reddit.client_id,
            client_secret=env.reddit.client_secret,
            user_agent=env.reddit.user_agent,
        )
        reddit.read_only = True

        return reddit

    def _get_subreddit(self, subreddit: str) -> Subreddit:
        """Get a specific subreddit given the subreddit identifier.

        Args:
            subreddit (str): The subreddit identifier.

        Returns:
            Subreddit: The Subreddit instance to use for fetching submissions.
        """

        return self.reddit.subreddit(subreddit)

    def _iter_hot_submissions(self, subreddit: str) -> Iterator[Submission]:
        """Iterate over hot subreddit submissions.

        Args:
            subreddit (str): The subreddit identifier.

        Yields:
            Submission: A hot submission from the provided subreddit.
        """

        return self._get_subreddit(subreddit).hot()

    def _iter_new_submissions(self, subreddit: str) -> Iterator[Submission]:
        """Iterate over new subreddit submissions.

        Args:
            subreddit (str): The subreddit identifier

        Yields:
            Submission: A new submission from the provided subreddit.
        """

        return self._get_subreddit(subreddit).new()

    def iter_artifacts(
        self,
        subreddit: str,
        subreddit_iteration_strategy: str = "new",
    ) -> Iterator[Artifact]:
        """Iterate over artifacts from a Reddit subreddit.

        Args:
            subreddit (str):
                The subreddit identifier.
            subreddit_iteration_strategy (str, optional):
                The strategy of subreddit submissions to iterate over.
                Defaults to "new".

        Raises:
            ValueError: If the given subreddit iteration strategy does not exist.

        Yields:
            Artifact: The discovered artifact from the given subreddit.
        """

        handlers = {"new": self._iter_new_submissions, "hot": self._iter_hot_submissions}
        handler = handlers.get(subreddit_iteration_strategy, None)
        if handler is None:
            raise ValueError(
                f"Subreddit iteration strategy {subreddit_iteration_strategy} is not supported"
            )

        with client.db_session(env.database_path) as session:
            for submission in handler(subreddit):
                if client.artifact_exists(
                    session,
                    Artifact.build_fingerprint(submission.url),
                ):
                    continue

                yield client.ensure_artifact(session, submission.url)
