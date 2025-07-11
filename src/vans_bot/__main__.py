import logging
import os
import time
from slack_sdk import WebClient

from vans_bot.vans_lcp_faq import VansLcpFaqMonitor
from vans_bot.vans_lead_times import VansLeadTimeMonitor
from vans_bot.vans_news import VansNewsMonitor

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

channel_id = os.getenv("SLACK_CHANNEL_ID")
slack_token = os.getenv("SLACK_BOT_TOKEN")
update_freq = int(os.getenv("UPDATE_FREQ", 5 * 60))

assert channel_id is not None
assert slack_token is not None


def main():
    client = WebClient(token=slack_token)
    monitors = [VansNewsMonitor(), VansLeadTimeMonitor(), VansLcpFaqMonitor()]

    while True:
        logger.info("Checking for messages")
        for monitor in monitors:
            try:
                for message in monitor.check_for_messages():
                    client.chat_postMessage(
                        channel=channel_id, text=f"<!channel> {message}"
                    )
            except Exception as e:
                logger.warning(f"Error checking for messages in monitor {monitor}")
                logger.warning(e)

        time.sleep(update_freq)


if __name__ == "__main__":
    main()
