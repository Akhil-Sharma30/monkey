# serpentarium must be the first import, as it needs to save the state of the
# import system prior to any imports
# isort: off
import serpentarium  # noqa: F401
from serpentarium.logging import configure_host_process_logger

# isort: on
import argparse
import logging
import logging.handlers
import os
import sys
import traceback
from multiprocessing import Queue, freeze_support, get_context
from pathlib import Path
from typing import Sequence, Tuple, Union

# dummy import for pyinstaller
# noinspection PyUnresolvedReferences
from common.version import get_version
from infection_monkey.dropper import MonkeyDrops
from infection_monkey.model import DROPPER_ARG, MONKEY_ARG
from infection_monkey.monkey import InfectionMonkey
from infection_monkey.utils.monkey_log_path import get_agent_log_path, get_dropper_log_path


def main():
    freeze_support()  # required for multiprocessing + pyinstaller on windows

    mode, mode_specific_args = _parse_args()

    # TODO: Use an Enum for this
    if mode not in [MONKEY_ARG, DROPPER_ARG]:
        raise ValueError(f'The mode argument must be either "{MONKEY_ARG}" or "{DROPPER_ARG}"')

    multiprocessing_context = get_context(method="spawn")
    ipc_logger_queue = multiprocessing_context.Queue()

    log_path = _get_log_file_path(mode)

    queue_listener = _configure_queue_listener(ipc_logger_queue, log_path)
    queue_listener.start()

    logger = _configure_logger()
    logger.info(f"writing log file to {log_path}")

    try:
        _run_agent(mode, mode_specific_args, ipc_logger_queue, logger)
    except Exception as err:
        logger.exception(f"An unexpected error occurred while running the agent: {err}")
    finally:
        queue_listener.stop()


def _parse_args() -> Tuple[str, Sequence[str]]:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "mode",
        choices=[MONKEY_ARG, DROPPER_ARG],
        help=f"'{MONKEY_ARG}' mode will run the agent in the current session/terminal."
        f"'{DROPPER_ARG}' will detach the agent from the current session "
        f"and will start it on a separate process.",
    )
    mode_args, mode_specific_args = arg_parser.parse_known_args()
    mode = str(mode_args.mode)

    return mode, mode_specific_args


def _get_log_file_path(mode: str):
    if MONKEY_ARG == mode:
        return get_agent_log_path()

    return get_dropper_log_path()


def _configure_queue_listener(
    ipc_logger_queue: Queue, log_file_path: Path
) -> logging.handlers.QueueListener:
    """
    Gets unstarted configured QueueListener object

    We configure the root logger to use QueueListener with Stream and File handler.

    :param ipc_logger_queue: A Queue shared by the host and child process that stores log messages
    :param log_path: A Path used to configure the FileHandler
    """
    log_format = (
        "%(asctime)s [%(process)d:%(threadName)s:%(levelname)s] %(module)s.%("
        "funcName)s.%(lineno)d: %(message)s"
    )
    formatter = logging.Formatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)

    queue_listener = configure_host_process_logger(ipc_logger_queue, [stream_handler, file_handler])
    return queue_listener


def _configure_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    def log_uncaught_exceptions(ex_cls, ex, tb):
        logger.critical("".join(traceback.format_tb(tb)))
        logger.critical("{0}: {1}".format(ex_cls, ex))

    sys.excepthook = log_uncaught_exceptions

    return logger


def _run_agent(
    mode: str,
    mode_specific_args: Sequence[str],
    ipc_logger_queue: Queue,
    logger: logging.Logger,
):
    logger.info(
        ">>>>>>>>>> Initializing the Infection Monkey Agent: PID %s <<<<<<<<<<", os.getpid()
    )

    logger.info(f"version: {get_version()}")

    monkey: Union[InfectionMonkey, MonkeyDrops]
    if MONKEY_ARG == mode:
        monkey = InfectionMonkey(mode_specific_args, ipc_logger_queue=ipc_logger_queue)
    elif DROPPER_ARG == mode:
        monkey = MonkeyDrops(mode_specific_args)

    try:
        logger.info(f"Starting {monkey.__class__.__name__}")
        monkey.start()
    except Exception as err:
        logger.exception("Exception thrown from monkey's start function. More info: {}".format(err))

    try:
        monkey.cleanup()
    except Exception as err:
        logger.exception(
            "Exception thrown from monkey's cleanup function: More info: {}".format(err)
        )


if "__main__" == __name__:
    main()
