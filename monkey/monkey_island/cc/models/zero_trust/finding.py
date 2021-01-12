# coding=utf-8
"""
Define a Document Schema for Zero Trust findings.
"""

from __future__ import annotations
from typing import Union

from mongoengine import Document, GenericLazyReferenceField, StringField

import common.common_consts.zero_trust_consts as zero_trust_consts
# Dummy import for mongoengine.
# noinspection PyUnresolvedReferences
from monkey_island.cc.models.zero_trust.monkey_finding_details import MonkeyFindingDetails
from monkey_island.cc.models.zero_trust.scoutsuite_finding_details import ScoutSuiteFindingDetails


class Finding(Document):
    """
    This model represents a Zero-Trust finding: A result of a test the monkey/island might perform to see if a
    specific principle of zero trust is upheld or broken.

    Findings might have the following statuses:
        Failed ❌
            Meaning that we are sure that something is wrong (example: segmentation issue).
        Verify ⁉
            Meaning that we need the user to check something himself (example: 2FA logs, AV missing).
        Passed ✔
            Meaning that we are sure that something is correct (example: Monkey failed exploiting).

    This class has 2 main section:
        *   The schema section defines the DB fields in the document. This is the data of the object.
        *   The logic section defines complex questions we can ask about a single document which are asked multiple
            times, or complex action we will perform - somewhat like an API.
    """
    # SCHEMA
    test = StringField(required=True, choices=zero_trust_consts.TESTS)
    status = StringField(required=True, choices=zero_trust_consts.ORDERED_TEST_STATUSES)
    finding_type = StringField(required=True, choices=zero_trust_consts.FINDING_TYPES)
    details = GenericLazyReferenceField(choices=[MonkeyFindingDetails, ScoutSuiteFindingDetails], required=True)
    # http://docs.mongoengine.org/guide/defining-documents.html#document-inheritance
    meta = {'allow_inheritance': True}

    # LOGIC
    def get_test_explanation(self):
        return zero_trust_consts.TESTS_MAP[self.test][zero_trust_consts.TEST_EXPLANATION_KEY]

    def get_pillars(self):
        return zero_trust_consts.TESTS_MAP[self.test][zero_trust_consts.PILLARS_KEY]

    # Creation methods
    @staticmethod
    def save_finding(test: str,
                     status: str,
                     detail_ref: Union[MonkeyFindingDetails, ScoutSuiteFindingDetails]) -> Finding:
        finding = Finding(test=test,
                          status=status,
                          details=detail_ref,
                          finding_type=Finding._get_finding_type_by_details(detail_ref))
        finding.save()
        return finding

    @staticmethod
    def _get_finding_type_by_details(details: Union[MonkeyFindingDetails, ScoutSuiteFindingDetails]) -> str:
        if type(details) == MonkeyFindingDetails:
            return zero_trust_consts.MONKEY_FINDING
        else:
            return zero_trust_consts.SCOUTSUITE_FINDING
