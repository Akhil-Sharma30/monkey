import logging

from flask import make_response, request

from common.utils.exceptions import AlreadyRegisteredError, InvalidRegistrationCredentialsError
from monkey_island.cc.resources.AbstractResource import AbstractResource
from monkey_island.cc.resources.auth.credential_utils import get_username_password_from_request
from monkey_island.cc.services import AuthenticationService

logger = logging.getLogger(__name__)


class Registration(AbstractResource):

    urls = ["/api/registration"]

    def get(self):
        return {"needs_registration": AuthenticationService.needs_registration()}

    def post(self):
        username, password = get_username_password_from_request(request)

        try:
            AuthenticationService.register_new_user(username, password)
            return make_response({"error": ""}, 200)
        # API Spec: HTTP status code for AlreadyRegisteredError should be 409 (CONFLICT)
        except (InvalidRegistrationCredentialsError, AlreadyRegisteredError) as e:
            return make_response({"error": str(e)}, 400)
