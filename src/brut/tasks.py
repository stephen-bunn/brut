# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

from .db import Content, db_session
from .env import instance as env
from .helpers import setup_logging
from .integrations import get_integration
from .log import instance as log

# brut.tasks is an entrypoint for workers, ensure logging is setup early
setup_logging()

redis_backend = RedisBackend()
redis_broker = RedisBroker(url=env.redis.url)
redis_broker.add_middleware(Results(backend=redis_backend))

dramatiq.set_broker(redis_broker)


@dramatiq.actor
def handle_content(integration_type: str, *args, **kwargs):
    integration = get_integration(integration_type)
    if integration is None:
        log.error(
            f"Failed to determine the appropriate integration for {integration_type!r}"
        )
        return None

    handler = integration()

    with db_session() as session:
        for content in handler.iter_content(*args, **kwargs):
            if session.query(
                session.query(Content)
                .filter(Content.fingerprint == content.fingerprint)
                .exists()
            ).scalar():
                log.debug(
                    f"Skipping content {content.url} ({content.fingerprint}) "
                    "as it already exists"
                )
                continue

            log.info(f"Adding content {content.url} ({content.fingerprint})")
            session.add(content)

        session.commit()
