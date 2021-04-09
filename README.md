# Brut

[![Test Status](https://github.com/stephen-bunn/brut/workflows/Test%20Package/badge.svg)](https://github.com/stephen-bunn/brut)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> Personal media archive toolset.

## Setup

- Install Docker & `docker-compose`.
- Setup environment variables in `./.env`

```ini
APP_DB_URL=sqlite:///data/brut.db
APP_LOG_DIR=/code/data/logs
APP_REDIS_URL=redis://redis:6379/0

# reddit configuration
APP_REDDIT_CLIENT_ID={Reddit app client id}
APP_REDDIT_CLIENT_SECRET={Reddit app client secret}
APP_REDDIT_USER_AGENT=Brut Archive Toolset by /u/{Reddit username that owns client_id}

APP_CONFIG_PATH=/code/brut.yml
```

- Setup application configuration in `./brut.yml`

```yaml
watch:
  - name: Reddit /r/apexlegends
    type: subreddit
    args:
      - apexlegends
    schedule:
      interval:
        minutes: 1
  - name: Reddit /r/apexuniversity
    type: subreddit
    args:
      - apexuniversity
    schedule:
      crontab: */5 * * * *
```

- Start up the tool using `docker-compose`.

```console
$ docker-compose build
... build ...
$ docker-compose up
... start ...
```
