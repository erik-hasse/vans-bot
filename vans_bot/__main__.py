import logging
import os
import time
from dotenv import load_dotenv
from slack_sdk import WebClient

from vans_bot.vans_news import VansNewsMonitor

logger = logging.getLogger(__name__)

load_dotenv()

channel_id = os.getenv("SLACK_CHANNEL_ID")


def main():
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    monitors = [VansNewsMonitor()]

    while True:
        for monitor in monitors:
            try:
                for message in monitor.check_for_messages():
                    client.chat_postMessage(channel=channel_id, text=message)
            except Exception as e:
                logger.warning(f"Error checking for messages in monitor {monitor}")
                logger.warning(e)

        time.sleep(60)


if __name__ == "__main__":
    main()
