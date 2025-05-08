import requests
import json
import logging

logger = logging.getLogger(__name__)

from dispatch.config import (
    ODOO_HOST,
    ODOO_DB,
    ODOO_USERNAME,
    ODOO_PASSWORD,
)

def odoo_authenticate() -> int:
    try:
        if not ODOO_HOST or not ODOO_DB or not ODOO_USERNAME or not ODOO_PASSWORD:
            raise Exception(f"odoo config get failed")

        url = ODOO_HOST + '/jsonrpc'
        headers = {'Content-Type': 'application/json'}

        auth_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}],
            },
            "id": 1
        }

        auth_response = requests.post(url, data=json.dumps(auth_data), headers=headers)
        auth_result = auth_response.json()
        # print(auth_result)
        uid = auth_result.get('result')
        if not uid:
            raise Exception(f"odoo authenticate get uid failed")

        return uid
    except Exception as e:
        logger.error(f"odoo authenticate failed: {e}")
        raise

