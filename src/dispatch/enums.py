from enum import Enum
from pathlib import Path
import os

class FilePath(Enum):
    FILE = Path(__file__).resolve().parent.parent
    # 项目根目录
    PROJECT_ROOT_PATH = os.path.dirname(FILE)

    SRC_DISPATCH_PATH = os.path.join(PROJECT_ROOT_PATH, 'src/dispatch/')

    CPROFILE_RESULT_PATH = os.path.join(SRC_DISPATCH_PATH, 'cprofile_util/cprofile_result/')

    RESET_LOCATION_DATA_PATH = os.path.join(SRC_DISPATCH_PATH, 'contrib/import_data/area/')

    RESEND_MESSAGE_LOGS_PATH = os.path.join(SRC_DISPATCH_PATH, 'message_admin/message_send/send_logs/')

class Visibility(str, Enum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(str, Enum):
    term = "Term"
    definition = "Definition"
    worker = "Worker"
    team_contact = "Team"
    service = "Service"
    policy = "Policy"
    tag = "Tag"
    task = "Task"
    document = "Document"
    plugin = "Plugin"
    job = "Job"


class MillCodes(str, Enum):
    TBM = "TBM"
    SRSM = "SRSM"
    SKG = "SKG"
    SRM = "SRM"
    MSM = "MSM"
