from enum import Enum

class AutoPlanType(str, Enum):
    ROAD = "road"
    LOAD_INSTRUCTIONS = "load_instructions"