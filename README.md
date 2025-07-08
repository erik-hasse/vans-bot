# Van's RV Slack Bot

Post news to the [Van's RV Slack group](https://join.slack.com/t/vansrv/shared_invite/zt-21llev8ir-fVi6lalTzDn_WAG6chVviQ).

## Installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) then run
```shell
uv sync
uvx pre-commit install
```

## Usage

Create a file named `.env` with the following values set:

```shell
SLACK_BOT_TOKEN=
SLACK_CHANNEL_ID=
```

Then run
```shell
uv run vans-bot  # Add `&` to the end to run in the background
```

## Deploying

```shell
TAG=10
docker build -t vans-bot:$TAG --platform linux/amd64 .
docker save -o export.tar vans-bot:$TAG
```

In Portainer, import the image, then edit the deployment with the new tag.
Be sure to uncheck "Always pull the image."
Verify that the service started in the logs.
