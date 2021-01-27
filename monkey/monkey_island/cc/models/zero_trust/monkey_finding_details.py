from __future__ import annotations

from typing import List

from mongoengine import Document, EmbeddedDocumentListField

from monkey_island.cc.models.zero_trust.event import Event


class MonkeyFindingDetails(Document):

    # SCHEMA
    events = EmbeddedDocumentListField(document_type=Event, required=False)

    # LOGIC
    def add_events(self, events: List[Event]) -> MonkeyFindingDetails:
        self.update(push_all__events=events)
        return self
