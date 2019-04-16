import abc
import logging
from typing import Callable, Dict, Iterable

_LOG = logging.getLogger(__name__)


class Bot(abc.ABC):
    commands: Dict[str, Callable] = {}

    @staticmethod
    def register_command(command: str) -> Callable:
        def wrapper(command_func: Callable) -> None:
            if command in Bot.commands:
                _LOG.error("command %s already registered", command)
                raise ValueError(f"command {command} already registered")
            Bot.commands[command] = command_func
            _LOG.debug("registered command %s", command)

        return wrapper

    def handle_command(self, command: str, command_args: str) -> str:
        if command in self.commands:
            _LOG.debug("handling command %s with args %s", command, command_args)
            return self.commands[command](self, command_args)
        response = f"command {command} not registered"
        _LOG.info(response)
        return response

    @abc.abstractmethod
    def run(self) -> None:
        pass
