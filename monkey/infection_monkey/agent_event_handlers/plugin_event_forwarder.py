import logging
import queue
from contextlib import suppress
from multiprocessing import Queue
from threading import Event

from common.event_queue import IAgentEventQueue
from infection_monkey.utils.threading import create_daemon_thread

logger = logging.getLogger(__name__)

QUEUE_EVENT_TIMEOUT = 2


class PluginEventForwarder:
    """
    Publishes events from the Agent's Plugin queue to the Agent's Event queue
    """

    def __init__(
        self,
        queue: Queue,
        agent_event_queue: IAgentEventQueue,
        queue_event_timeout: float = QUEUE_EVENT_TIMEOUT,
    ):
        self._queue = queue
        self._agent_event_queue = agent_event_queue
        self._queue_event_timeout = queue_event_timeout

        self._thread = create_daemon_thread(target=self.run, name="PluginEventForwarder")
        self._stop = Event()

    def start(self):
        self._stop.clear()
        self._thread.start()

    def run(self):
        logger.info("Starting plugin event forwarder")

        while not self._stop.is_set():
            with suppress(queue.Empty):
                event = self._queue.get(timeout=self._queue_event_timeout)
                self._agent_event_queue.publish(event)

    def stop(self, timeout=None):
        logger.info("Stopping plugin event forwarder")
        self._stop.set()
        self._thread.join(timeout)
