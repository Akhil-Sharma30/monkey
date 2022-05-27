import json

from monkey_island.cc.resources.AbstractResource import AbstractResource
from monkey_island.cc.resources.request_authentication import jwt_required
from monkey_island.cc.services.zero_trust.monkey_findings.monkey_zt_finding_service import (
    MonkeyZTFindingService,
)


class ZeroTrustFindingEvent(AbstractResource):
    # API Spec: Why is the endpoint separated? Why not just
    # "/api/zero-trust-finding-event/<string:finding_id>"?
    urls = ["/api/zero-trust/finding-event/<string:finding_id>"]

    @jwt_required
    def get(self, finding_id: str):
        return {
            "events_json": json.dumps(
                MonkeyZTFindingService.get_events_by_finding(finding_id), default=str
            )
        }
