import threading
import time

from slack import SlackBot
from fire import Fire

from client import CLI


class QBot(SlackBot):
    watch_timeout = 3

    def __init__(
        self, slack_api_token=None, slack_token_file=None, arsenal_token_file=None
    ):
        """
        Initialize QBot
        """
        self.cli = CLI(api_key_file=arsenal_token_file, enable_color=False)
        if slack_api_token is not None:
            SlackBot.__init__(self, slack_api_token=slack_api_token)
        else:
            SlackBot.__init__(self, slack_token_file=slack_token_file)

    def commands(self, command, channel):
        """
        Look for commands.
        """
        if command.startswith("arsenal "):
            # remove arsenal from the command and strip out extra spaces
            command = " ".join(command.split()[1:]).strip()
            self._logger.info("running arsenal command: {}".format(command))
            return self.handle_arsenal_command(command, channel)

    def handle_arsenal_command(self, command, channel):
        """
        Handle arsenal commands.
        """
        output = ""
        try:
            Fire(self.cli, "{}".format(command))

            output = "\n".join(self.cli._output_lines)
            self.cli._output_lines = []
        except:
            output = "oops That command is not supported"

        return output


if __name__ == "__main__":
    q = QBot(arsenal_token_file=".arsenal_key", slack_token_file=".slack_key")
    q.set_log_level("DEBUG")
    q.run()
