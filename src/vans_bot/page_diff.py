import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI()
prompt = """In 1 to 5 bullet points, summarize the changes to this webpage.
Only mention changes to user-facing content, not technical changes.
If there are no user-facing changes, then state that they are only technical changes:

# Old Version
{old}

# New Version
{new}
"""


def get_changes(old: str, new: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[dict(role="user", content=prompt.format(old=old, new=new))],
    )
    logger.info(
        f"Used {response.usage.prompt_tokens} prompt and "
        f"{response.usage.completion_tokens} completion tokens"
    )
    return response.choices[0].message.content
