# from pydantic.errors import PydanticValueError

from pydantic.errors import PydanticUserError

class DispatchException(Exception):
    pass


class InvalidConfiguration(DispatchException):
    pass


class InvalidFilterPolicy(DispatchException):
    pass


class DispatchPluginException(DispatchException):
    pass


class NotFoundError(PydanticUserError):
    code = "not_found"
    msg_template = "{msg}"


class FieldNotFoundError(PydanticUserError):
    code = "not_found.field"
    msg_template = "{msg}"


class InvalidFilterError(PydanticUserError):
    code = "invalid.filter"
    msg_template = "{msg}"
