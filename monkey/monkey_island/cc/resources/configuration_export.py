import json

import flask_restful
from flask import request

from monkey_island.cc.resources.auth.auth import jwt_required
from monkey_island.cc.services.config import ConfigService
from monkey_island.cc.services.utils.encryption import encrypt_string


class ConfigurationExport(flask_restful.Resource):
    @jwt_required
    def post(self):
        data = json.loads(request.data)
        should_encrypt = data["should_encrypt"]

        plaintext_config = ConfigService.get_config()

        config_export = plaintext_config
        if should_encrypt:
            password = data["password"]
            plaintext_config = json.dumps(plaintext_config)
            config_export = encrypt_string(plaintext_config, password)

        return {"config_export": config_export, "encrypted": should_encrypt}
