import logging

from common.version import get_version
from monkey_island.cc.resources.AbstractResource import AbstractResource
from monkey_island.cc.services.version_update import VersionUpdateService

logger = logging.getLogger(__name__)


class VersionUpdate(AbstractResource):
    # API Spec: Rename to /version-info
    urls = ["/api/version-update"]

    def __init__(self):
        super(VersionUpdate, self).__init__()

    # We don't secure this since it doesn't give out any private info and we want UI to know version
    # even when not authenticated
    def get(self):
        return {
            "current_version": get_version(),
            "newer_version": VersionUpdateService.get_newer_version(),
            "download_link": VersionUpdateService.get_download_link(),
        }
