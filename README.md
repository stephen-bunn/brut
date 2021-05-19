# Brut

[![Test Status](https://github.com/stephen-bunn/brut/workflows/Test%20Package/badge.svg)](https://github.com/stephen-bunn/brut)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> Personal media archive toolset.

## Setup

- Install Docker & `docker-compose`.
- Setup environment variables in `./.env`

```ini
# The path to where the brut.yml config was copied during the container build
APP_CONFIG_PATH=/code/brut.yml
```

- Setup application configuration in `./brut.yml`

```yaml
db: sqlite:///data/brut.db  # The database URL for data persistence
redis: redis://redis:6379/0  # The Redis URL to attach to for job management
store: /data  # The directory where artifacts should be persisted

# Defines logging setup for logs emitted by Brut
log:
  dir: /code/data/logs

# Watchers defines configuration necessary for various supported watcher types
watchers:
  reddit:
    client_id: [Reddit CLIENT_ID]  # The CLIENT_ID for your Reddit app
    client_secret: [Reddit CLIENT_SECRET]  # The CLIENT_SECRET for your Reddit app
    user_agent: [Reddit user agent]  # The user-agent reported to Reddit

# Watch defines what information from the web will be polled on what schedule
watch:
  - name: Reddit /r/apexlegends  # a user-friendly name for logging purposes
    type: subreddit  # uses the subreddit watcher type
    args:
      - apexlegends  # monitors the subreddit /r/apexlegends
    schedule:
      interval:
        minutes: 1  # fires every minute
      immediate: true  # fires immediately on creation of the watch

  - name: Reddit /r/apexuniversity
    type: subreddit
    args:
      - apexuniversity
    schedule:
      crontab: */5 * * * *  # fires every 5 minutes

# Enqueue is how often we scan and queue new Content entries produced by watchers
# to be fetched and persisted to the store
enqueue:
  interval:
    minutes: 5
```

- Start up the tool using `docker-compose`.

```console
$ docker-compose build
... build ...
$ docker-compose up
... start ...
```
