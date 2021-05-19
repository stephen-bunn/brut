# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Recalculate all content fingerprints."""

from brut.db import Content, Artifact, db_session
from brut.log import instance as log


def recalculate_fingerprints():
    """Recalculate all content fingerprints."""

    seen_fingerprints = set()
    with db_session() as session:
        for content in session.query(Content).all():
            log.info(f"Recalculating fingerprint for content {content.id}")
            fingerprint = Content.build_fingerprint(content.url)
            if fingerprint in seen_fingerprints:
                log.warning(
                    "Removing duplicate artifact+content for fingerprint "
                    f"{fingerprint}"
                )
                session.query(Artifact).filter(
                    Artifact.content_id == content.id
                ).delete()
                session.delete(content)
            else:
                content.fingerprint = Content.build_fingerprint(content.url)
                seen_fingerprints.add(content.fingerprint)


if "__main__" in __name__:
    recalculate_fingerprints()
