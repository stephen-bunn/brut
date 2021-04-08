# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

import abc
from io import BytesIO
from typing import Generator

from ..db import Content
from ..hasher import HashType, hash_io
from ..log import instance as log


class BaseIntegration(abc.ABC):
    @abc.abstractproperty
    def name(self) -> str:
        raise NotImplementedError()

    def get_fingerprint(self, source: str, source_id: str) -> str:
        fingerprint = hash_io(
            BytesIO(bytes(f"{source!s}|{source_id!s}", "utf-8")), {HashType.SHA256}
        )[HashType.SHA256]
        log.debug(
            f"Computed fingerprint for ({source!r}, {source_id!r}) as {fingerprint!r}"
        )

        return fingerprint

    @abc.abstractmethod
    def iter_content(self, *args, **kwargs) -> Generator[Content, None, None]:
        raise NotImplementedError()
