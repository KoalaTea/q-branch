"""
A module providing useful functionality for slackbots.
"""
import os
import logging
import time
import threading
from slackclient import SlackClient

#TODO config

class SlackBot(object):
    bot_id = 'alkgj;oianrg;kncvniuahiuh84hui3ngk,ajvhiu'
    username = 'q'
    _handler = logging.StreamHandler()
    _logger = logging.getLogger(__name__)
    _logger.addHandler(_handler)
    _logger.setLevel('INFO')

    def __init__(self, slack_api_token=None, slack_token_file=None):
        if slack_api_token is None:
            slack_api_token = self._get_token(slack_token_file)

        # Initialize slack client
        self.slack_client = SlackClient(slack_api_token)
        self._init_bot_id()

    def _get_token(self, slack_token_file=None):
        """
        Attempt to fetch a token from a file.
        """
        # Attempt to read token from file
        if slack_token_file and os.path.exists(slack_token_file):
            with open(slack_token_file, 'r') as keyfile:
                api_token = keyfile.readlines()[0].strip().strip('\n')

        return api_token

    def set_log_level(self, level):
        self._logger.setLevel(level)

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        #TODO channel protections
        self._logger.info('handling command: {}'.format(command))
        answer = None
        if command.startswith('Q?'):
            joel_id = self.get_user_id('joel')
            answer = "Beep Boop I'm Joe Graham. <@{}>".format(joel_id)
        elif command.startswith('q?'):
            joe_id = self.get_user_id('joe_graham')
            answer = "Beep Boop I'm Joe Graham. <@{}>".format(joe_id)
        elif command.startswith('rip'):
            answer = 'qq more scrub'
        else:
            answer = self.commands(command, channel)

        if answer:
            self.send_message(channel, 'Response to *{}* command'.format(command))
            self.send_message(channel, answer)

    def commands(self, command, channel):
        """ here for others to implement in inherited classes """
        return ''

    def send_message(self, channel, msg):
        self.slack_client.api_call("chat.postMessage", channel=channel, text=msg, as_user=True)

    def get_user_id(self, username):
        users = self.slack_client.api_call('users.list')['members']
        for user in users:
            if user['name'] == username:
                return user['id']

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        self._logger.debug(slack_rtm_output)
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.bot_id in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.bot_id)[1][1:].strip(), output['channel']
        return None, None

    def _init_bot_id(self):
        users = self.slack_client.api_call('users.list')['members']
        for user in users:
            if user['name'] == self.username:
                self.bot_id = user['id']
                self._logger.info('bot_id: {}'.format(self.bot_id))
                return

    def run(self):
        READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
        if self.slack_client.rtm_connect():
            self._logger.info("StarterBot connected and running!")
            while True:
                command, channel = self.parse_slack_output(self.slack_client.rtm_read())
                if command and channel:
                    #threading.Thread(target=self.handle_command, args=(command, channel,)).start()
                    self.handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            self._logger.critical("Connection failed. Invalid Slack token or bot ID?")
