import logging
from q_branch import slack

_LOG = logging.getLogger(__name__)


def main():
    logging.basicConfig(level="DEBUG")
    from examples import qbot

    _LOG.info("initializing q bot")
    q = slack.SlackBot(slack_token_file=".slack_key")
    _LOG.info("running q bot")
    q.run()


if __name__ == "__main__":
    main()
