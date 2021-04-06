# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""This module contains project tests and is declared to allow for relative imports."""

import os
import sys

from hypothesis import HealthCheck, settings

settings.register_profile("default", max_examples=30)
settings.register_profile(
    "ci",
    suppress_health_check=[HealthCheck.too_slow],
    max_examples=30,
    deadline=None,
)
settings.register_profile(
    "windows",
    suppress_health_check=[HealthCheck.too_slow],
    max_examples=10,
    deadline=None,
)

settings.load_profile("default")

if sys.platform in ("win32",):
    settings.load_profile("windows")

# NOTE: this is currently tailored for Github actions
if os.environ.get("CI", None) == "true":
    settings.load_profile("ci")
