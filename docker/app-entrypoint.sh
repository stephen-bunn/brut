#!/bin/sh

# run database migrations
/code/.venv/bin/python -m alembic upgrade head

# run application
/code/.venv/bin/python -m brut.app

