from enum import Enum


class FinishedProductStatusEnum(str, Enum):
    """
    Enum for finished product status
    """
    CREATED = "created"
    DESPATCHED = "despatched"
    ARCHIVED = "archived"
    RETURNED = "returned"


class FinishedProductStockTypeEnum(str, Enum):
    """
    Enum for finished product stock type
    """
    INTERNAL = "internal"


class FinishedProductExistFlagEnum(str, Enum):
    """
    Enum for finished product exist flag
    """
    EXIST = "Y"
    NOT_EXIST = "N"


class FinishedProductTypeEnum(str, Enum):
    """
    Enum for finished product type
    """
    BUNDLE = "bundle"
