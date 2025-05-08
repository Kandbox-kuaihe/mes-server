import logging

from starlette.config import Config


from dispatch.log import getLogger
log = getLogger(__name__)


config = Config(env_file="dev.env")


DISPATCH_JWT_AUDIENCE = config("DISPATCH_JWT_AUDIENCE", default=None)
DISPATCH_JWT_EMAIL_OVERRIDE = config("DISPATCH_JWT_EMAIL_OVERRIDE", default=None)


if config.get("DISPATCH_AUTHENTICATION_PROVIDER_SLUG", default="dispatch-auth-provider-basic") == "dispatch-auth-provider-pkce":
    if not DISPATCH_JWT_AUDIENCE:
        log.warning("No JWT Audience specified. This is required for IdPs like Okta")
    if not DISPATCH_JWT_EMAIL_OVERRIDE:
        log.warning("No JWT Email Override specified. 'email' is expected in the idtoken.")
