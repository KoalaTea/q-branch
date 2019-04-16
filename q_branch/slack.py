"""
A module providing useful functionality for slackbots.
"""
import os
import logging
import time
import threading
from slackclient import SlackClient
from q_branch import bot
from typing import Optional, List, Dict, Any, Tuple

# TODO config

_LOG = logging.getLogger(__name__)


class SlackException(Exception):
    def __init__(self, api_method, err):
        self.api_method = api_method
        self.err = f"{err}"

    def __str__(self):
        return f"api call {self.api_method} returned error '{self.err}'"


class SlackBot(bot.Bot):
    bot_id: str
    username: str
    debug: bool

    def __init__(
        self, slack_api_token: str = "", slack_token_file: str = "", debug: bool = False
    ) -> None:
        self.debug = debug
        self.bot_id = ""
        self.username = ""
        if slack_api_token is None:
            slack_api_token = self._get_token(slack_token_file)

        # Initialize slack client
        self.slack_client = SlackClient(slack_api_token)
        self._init_bot_id()

    def _api_call(self, method, **kwargs):
        """ wrapper function on slack_client.api_call to do error checking """
        resp = self.slack_client.api_call(method, **kwargs)
        if not resp.get("ok"):
            error = resp.get(
                "error",
                "ok was false or missing from api_response but no error was included",
            )
            raise SlackException(method, error)
        return resp

    def _get_token(self, slack_token_file: str) -> str:
        """
        Attempt to fetch a token from a file.
        """
        # Attempt to read token from file
        if slack_token_file and os.path.exists(slack_token_file):
            with open(slack_token_file, "r") as keyfile:
                api_token = keyfile.readlines()[0].strip().strip("\n")

        return api_token

    def _init_bot_id(self) -> None:
        users = self._api_call("users.list")["members"]
        for user in users:
            if user["name"] == self.username:
                self.bot_id = user["id"]
                _LOG.info("bot_id: {}".format(self.bot_id))
                return

    def parse_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        # TODO channel protections
        _LOG.info("handling command: {}".format(command))
        try:
            command, command_args = command.split(maxsplit=1)
        except IndexError:
            command_args = ""
        answer = self.handle_command(command, command_args)
        if answer:
            self.send_message(channel, "Response to *{}* command".format(command))
            self.send_message(channel, answer)

    def send_message(self, channel: str, msg: str) -> None:
        try:
            self._api_call(
                "chat.postMessage", channel=channel, text=msg, as_user=True
            )
        except SlackException as e:
            _LOG.exception(e)

    def get_user_id(self, username: str) -> Optional[str]:
        """ gets the slack user id from the slack username """
        users = self._api_call("users.list")["members"]
        for user in users:
            if user["name"] == username:
                return user["id"]
        return None

    def parse_slack_output(
        self, slack_rtm_output: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
            Parses responses from the Slack Real Time Messaging API checking if any messages were
            directed at the bot. If a message was directed at the bot, it parses out everything
            after the @bot and returns that as the command along with the channel the message was
            made in.
        """
        _LOG.debug(slack_rtm_output)
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and "text" in output and self.bot_id in output["text"]:
                    # return text after the "@<botid>" mention, whitespace removed
                    return (
                        output["text"].split(self.bot_id)[1][1:].strip(),
                        output["channel"],
                    )
        return None, None

    def run(self) -> None:
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if self.slack_client.rtm_connect():
            _LOG.info("SlackBot connected and running!")
            while True:
                command, channel = self.parse_slack_output(self.slack_client.rtm_read())
                if command and channel:
                    if self.debug:
                        self.handle_command(command, channel)
                    else:
                        threading.Thread(
                            target=self.handle_command, args=(command, channel)
                        ).start()
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            _LOG.critical("Connection failed. Invalid Slack token or bot ID?")
