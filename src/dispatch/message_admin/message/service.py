from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from dispatch.system_admin.auth.models import DispatchUser
import logging

from dispatch.log import getLogger
log = getLogger(__name__)



def get_message_from_mq():
    pass
  