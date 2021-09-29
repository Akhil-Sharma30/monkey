import logging

from pymongo import errors

from monkey_island.cc.database import mongo
from monkey_island.cc.models.attack.attack_mitigations import AttackMitigations
from monkey_island.cc.services.attack.mitre_api_interface import MitreApiInterface
from monkey_island.cc.services.database import Database

logger = logging.getLogger(__name__)


def reset_database():
    Database.reset_db()
    if Database.is_mitigations_missing():
        logger.info("Populating Monkey Island with ATT&CK mitigations, this might take a while...")
        _try_store_mitigations_on_mongo()


def _try_store_mitigations_on_mongo():
    mitigation_collection_name = AttackMitigations.COLLECTION_NAME
    try:
        mongo.db.validate_collection(mitigation_collection_name)
        if mongo.db.attack_mitigations.count() == 0:
            raise errors.OperationFailure(
                "Mitigation collection empty. Try dropping the collection and running again"
            )
    except errors.OperationFailure:
        try:
            mongo.db.create_collection(mitigation_collection_name)
        except errors.CollectionInvalid:
            pass
        finally:
            _store_mitigations_on_mongo()


def _store_mitigations_on_mongo():
    stix2_mitigations = MitreApiInterface.get_all_mitigations()
    mongo_mitigations = AttackMitigations.dict_from_stix2_attack_patterns(
        MitreApiInterface.get_all_attack_techniques()
    )
    mitigation_technique_relationships = (
        MitreApiInterface.get_technique_and_mitigation_relationships()
    )
    for relationship in mitigation_technique_relationships:
        mongo_mitigations[relationship["target_ref"]].add_mitigation(
            stix2_mitigations[relationship["source_ref"]]
        )
    for relationship in mitigation_technique_relationships:
        mongo_mitigations[relationship["target_ref"]].add_no_mitigations_info(
            stix2_mitigations[relationship["source_ref"]]
        )
    for key, mongo_object in mongo_mitigations.items():
        mongo_object.save()
