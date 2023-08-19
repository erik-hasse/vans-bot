# Van's RV Slack Bot

Post news to the [Van's RV Slack group](https://join.slack.com/t/vansrv/shared_invite/zt-21llev8ir-fVi6lalTzDn_WAG6chVviQ).

## Installation

Install [poetry](https://python-poetry.org/docs/#installation) then run
```shell
poetry install --with dev
pre-commit install
```

## Usage

Create a file named `.env` with the following values set:

```shell
SLACK_BOT_TOKEN=
SLACK_CHANNEL_ID=
```

Then run
```shell
poetry run python -m vans_bot  # Add `&` to the end to run in the background
```
