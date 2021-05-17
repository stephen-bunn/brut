# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Recalculate all content fingerprints."""

from brut.db import Content, db_session
from brut.log import instance as log


def recalculate_fingerprints():
    """Recalculate all content fingerprints."""

    with db_session() as session:
        for content in session.query(Content).all():
            log.info(f"Recalculating fingerprint for content {content.id}")
            content.fingerprint = Content.build_fingerprint(content.url)


if "__main__" in __name__:
    recalculate_fingerprints()
