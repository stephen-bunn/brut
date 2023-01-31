#!/bin/sh

caribou upgrade $BRUT_DATABASE_PATH /code/brut/db/changes/
python -m brut.app
