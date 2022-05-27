import logging

from monkey_island.cc.resources.AbstractResource import AbstractResource
from monkey_island.cc.resources.request_authentication import jwt_required
from monkey_island.cc.services.island_logs import IslandLogService

logger = logging.getLogger(__name__)


class IslandLog(AbstractResource):
    # API Spec: Why the inconsistency in endpoints of IslandLog and Log?
    urls = ["/api/log/island/download"]

    @jwt_required
    def get(self):
        try:
            return IslandLogService.get_log_file()
        except Exception:
            logger.error("Monkey Island logs failed to download", exc_info=True)
