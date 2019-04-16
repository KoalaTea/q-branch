import threading
import time

from q_branch import bot
from q_branch.slack import SlackBot
from fire import Fire

import arsenal
import logging

_LOG = logging.getLogger(__name__)

# _LOG.debug("initializing arsenal CLI")
# CLI = arsenal.CLI(api_key_file=".arsenal_key", enable_color=False)
# _LOG.debug("initialized arsenal CLI")


@SlackBot.register_command("Q?")
def handle_Q(bot: SlackBot, command_args: str):
    joel_id = bot.get_user_id("joel")
    return f"Beep Boop I'm Joe Graham. <@{joel_id}>"


def handle_q(bot: SlackBot, command_args: str):
    joe_id = bot.get_user_id("joe_graham")
    return f"Beep Boop I'm Joe Graham. <@{joe_id}>"


@SlackBot.register_command("rip")
def handle_rip(bot: SlackBot, command_args: str):
    return "qq more scrub"


@SlackBot.register_command("arsenal")
def handle_arsenal_command(bot: SlackBot, command_args: str):
    """
    Handle arsenal commands.
    """
    output = ""
    try:
        Fire(CLI, f"{command_args[0]}")

        output = "\n".join(CLI._output_lines)
        CLI._output_lines = []
    except:
        output = f"oops arsenal command {command_args[0]} is not supported"

    return output


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    _LOG.info("initializing q bot")
    q = SlackBot(slack_token_file=".slack_key")
    _LOG.info("running q bot")
    q.run()
