# Brut

Simple content fetching application making use of [Megu](https://github.com/stephen-bunn/megu) to fetch media to a local storage volume.

## Configuration

This application is deployed using [Docker](https://www.docker.com/) which should be automated through [Docker Compose](https://docs.docker.com/compose/) through the included `docker-compose.yaml`.
Before you can successfully deploy this application, you will need to provide several pieces of configuration first.

### `brut.yaml`

In the root of the repository (next to the `docker-compose.yaml` file), you will need to create a `brut.yaml` config file to inform the application what resources it should be watching and fetching content for.
This is broken into two primary sections `watch` and `enqueue`.

```yaml
watch:
  - name: Reddit /r/apexlegends
    type: reddit
    args:
      - apexlegends
    schedule:
      crontab: "*/10 * * * *"
      immediate: false

enqueue:
  crontab: "*/5 * * * *"
  immediate: true
```

#### Watchers

The `watch` section of `brut.yaml` describes a list of watchers and their required configuration to scan a resource for artifacts (URLs).

> Currently only the `reddit` watcher type is included in the Brut application.

Given the following configuration:

```yaml
watch:
  - name: Reddit /r/apexlegends
    type: reddit
    args:
      - apexlegends
    schedule:
      crontab: "*/10 * * * *"
      immediate: false
```

We are creating a watcher of type `reddit` that passes the positional argument `apexlegends` to the application-included Reddit watcher.
The `name` is just a unique, user-friendly name that is used for scheduler and logging purposes.

The included `schedule` propery defines how often the `apexlegends` subreddit is scanned for new artifacts.
With the current crontab definition of `*/10 * * * *`, the subreddit is scanned every 10th minute.

> By default the Reddit watcher scans for new (latest) subreddit submissions.

If `schedule.immediate` is truthy, the subreddit watcher is triggered immediately once the scheduler is created.

#### Enqueue

The `enqueue` section of the `brut.yaml` configuration describes the schedule that discovered artifacts from the watchers are attempted to be fetched.

```yaml
enqueue:
  crontab: "*/5 * * * *"
  immediate: true
```

For example, given the crontab `*/5 * * * *`, unfetched artifacts are attempted to be fetched using Megu to the local storage directory every 5th minute.

If `immediate` is truthy, then the enqueue task is immediately triggered when the scheduler is created.

### Environment Variables

The application requires some user-provided environment variables for watcher credentials.
These should be provided in a `.env` file located in the root of this repository (next to the `docker-compose.yaml` file).
Required environment variables are the following:

```ini
# Required for Reddit watchers
BRUT_REDDIT_CLIENT_ID=<Reddit API client ID>
BRUT_REDDIT_CLIENT_SECRET=<Reddit API client secret>
BRUT_REDDIT_USER_AGENT=<Reddit application user agent>
```

## Run Application

If the appropriate configuration exists, all you should need to do to run the application is spin it up using Docker compose.

```console
$ docker compose up
```

This should start the task queue with the configured watchers and spin up monitoring that can be viewed on the included Grafana container.

This Grafana container should be hosted locally on port `:3000` by default (http://localhost:3000/).
