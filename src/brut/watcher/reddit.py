from functools import cached_property
from typing import Iterator

from praw import Reddit
from praw.models import Subreddit

from brut.config import get_config
from brut.db import client
from brut.db.models import Artifact
from brut.env import get_env
from brut.log import get_logger
from brut.types import WatcherProtocol

env = get_env()
log = get_logger()


class RedditWatcher(WatcherProtocol):
    type = "reddit"

    @cached_property
    def reddit(self) -> Reddit:
        config = get_config()["watchers"]["reddit"]

        log.debug(f"Building read-only Reddit client using id {config['client_id']}")
        reddit = Reddit(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_agent=config["user_agent"],
        )
        reddit.read_only = True

        return reddit

    def _get_subreddit(self, subreddit: str) -> Subreddit:
        return self.reddit.subreddit(subreddit)

    def _iter_hot_artifacts(self, subreddit: str) -> Iterator[Artifact]:
        return self._get_subreddit(subreddit).hot()

    def _iter_new_artifacts(self, subreddit: str) -> Iterator[Artifact]:
        return self._get_subreddit(subreddit).new()

    def iter_artifacts(
        self,
        subreddit: str,
        subreddit_iteration_strategy: str = "new",
    ) -> Iterator[Artifact]:
        handlers = {"new": self._iter_new_artifacts, "hot": self._iter_hot_artifacts}
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
