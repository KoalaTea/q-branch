import threading
import time

from slack import SlackBot
from fire import Fire

from client import CLI

class QBot(SlackBot):
    watch_timeout = 3

    def __init__(self, **kwargs):
        """
        Initialize QBot
        """
        self.cli = CLI(api_key_file=kwargs.get('arsenal_token_file'))
        SlackBot.__init__(self, **kwargs)

    def commands(self, command, channel):
        """
        Look for commands.
        """
        if command.startswith('arsenal '):
            # remove arsenal from the command and strip out extra spaces
            command = ' '.join(command.split()[1:]).strip()
            self._logger.info('running arsenal command: {}'.format(command))
            return self.handle_arsenal_command(command, channel)

    def handle_arsenal_command(self, command, channel):
        """
        Handle arsenal commands.
        """
        fire.Fire(self.cli, '{}'.format(self._cmd))

        output = '\n'.join(self.cli._output_lines)
        self.cli._output_lines = []

        return output

if __name__ == '__main__':
    q = QBot(arsenal_token_file='.arsenal_key', slack_token_file='.slack_key')
    q.set_log_level('DEBUG')
    q.run()
