import os
import sys
from fastapi.testclient import TestClient

os.environ["DATABASE_NAME"] = 'dispatch'
os.environ['REDIS_DB'] = '1'
from dispatch.main import app
from dispatch.log import getLogger
from sqlalchemy import text, create_engine
from sqlalchemy_utils import database_exists, drop_database

current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(current_path)))
from dispatch.database_util.service import get_schema_session
from dispatch.log import getLogger
log = getLogger(__name__)
from dispatch.config import DISPATCH_JWT_SECRET 

from dispatch.config import SQLALCHEMY_DATABASE_URI, DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_CREDENTIALS
logger = getLogger(__name__)

test_database_name = os.environ["DATABASE_NAME"]
db_url = SQLALCHEMY_DATABASE_URI


class OverAllAPI:
    db_session = get_schema_session(org_code="mes_root")    
    advice_id = None
    t1_area_id = None

    def login(self):
        login_data = {"email": "mes_root@kuaihe.tech", "password":  DISPATCH_JWT_SECRET}
        response = self.client.post(self.host_url + "/auth/login", json=login_data)
        assert response.status_code == 200
        assert response.json()["message"] == 'succeed'
        self.token = response.json()["data"]["token"]
        log.debug(f"token: {self.token}")
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
    
    
    def init_settings(self):
        resp = self.client.post(self.host_url + "/menu/data/init_menu_button_settings", json={}, headers=self.headers)
        assert resp.status_code == 200
        log.debug(f"init_settings: {resp.json()}")
    
    def update_user_mill(self, mill_id=410):
        # 更新用户当前mill_id
        resp = self.client.post(self.host_url + f"/user/new_update_user_mill/{mill_id}", json={}, headers=self.headers)
        assert resp.status_code == 200
    

    def check_database_exists(db_name):
        try:
            # 使用 sqlalchemy_utils 检查数据库是否存在
            exists = database_exists(db_url)
            if exists:
                logger.info(f"Database {db_name} exists")
            else:
                logger.info(f"Database {db_name} does not exist")
            return exists
        except Exception as e:
            logger.error(f"Error checking database existence: {e}")
            return False
        
    
    def delete_database(self):
        try:
            if database_exists(db_url):
                # 终止所有连接到 test_database 的会话
                admin_engine = create_engine(f"postgresql://{DATABASE_CREDENTIALS}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/postgres")
                with admin_engine.begin() as conn:
                    conn.execute(text(f"""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = '{test_database_name}'
                        AND pid <> pg_backend_pid()
                    """))
                
                # 删除数据库
                drop_database(db_url)
            if not database_exists(db_url):
                logger.info(f"Database {test_database_name} removed successfully")
        except Exception as e:
            logger.error(f"Error deleting database: {e}")

    def test_semi_all(self):
        try:
            from dispatch.database_util.manage import init_database
            test_engine = create_engine(db_url)
            init_database(test_engine,db_url)
        except Exception as e:
            logger.error(f"Error creating database: {e}")

        self.token = None
        self.client = TestClient(app)
        self.host_url = "http://localhost:7999/api/v1"
        self.login()
        self.init_settings()

        # create mill(SCT)
        data = {
            "code": "SCT",
            "desc": "Mill test",
            "type": "SCT",
            "user_ids": [
                1
            ],
            "dispatch_user": [
                {
                    "updated_at": "2024-10-23T12:20:30.608179",
                    "updated_by": None,
                    "created_at": "2024-10-23T12:20:30.608182",
                    "created_by": None,
                    "is_deleted": 0,
                    "flex_form_data": {},
                    "email": "mes@kuaihe.tech",
                    "is_active": True,
                    "id": 1,
                    "org_id": 101,
                    "org_code": "mes_root",
                    "default_team_id": 1,
                    "current_mill_id": 1,
                    "current_mill_code": "SCT",
                    "current_menu_path": "/",
                    "is_org_owner": True,
                    "is_team_owner": False,
                    "thumbnail_photo_url": "",
                    "full_name": None,
                    "role": [
                        {
                            "updated_at": "2025-04-17T01:11:32.949332",
                            "updated_by": "mes_root@kuaihe.tech",
                            "created_at": "2024-10-23T12:20:32.331951",
                            "created_by": "mes_root@kuaihe.tech",
                            "is_deleted": 0,
                            "flex_form_data": {},
                            "name": "sys",
                            "key": "sys",
                            "sort": 1,
                            "status": True,
                            "admin": True,
                            "remark": "System role",
                            "homepage_path": True,
                            "id": 1
                        }
                    ],
                    "show_bottom_note": True
                }
            ]
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/mill", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200

        self.update_user_mill(1)


        #create site_type
        data = {
            "code": "SCT",
            "mill_code": "SCT",
            "mill_id": 1,
            "name": "site_type",
            "business_type": "s-semi",
            "desc": None,
            "latitude": "2",
            "longitude": "1",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/site_type", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200
        assert response.json()['name'] == "site_type"

        # create site
        data = {
            "code": "aaa",
            "name": "site",
            "desc": None,
            "site_type_code": "SCT",
            "mill_id": 1,
            "latitude": "2",
            "longitude": "1",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/site/", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200
        assert response.json()['name'] == "site"

        # 1. 创建area: D1 (charge_status = N), S1  (charge_status = Y), S2  (charge_status = Y)
        # D1
        data = {
            "code": "D1",
            "type": "s-semi",
            "desc": None,
            "site_code": "aaa",
            "charge_status": "Y",
            "mill_id": 1,
            "latitude": "2",
            "longitude": "1",
            "updated_at": None,
            "updated_by": None,
            "actions": "Action",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/area", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200
        assert response.json()['code'] == "D1"
        assert response.json()['charge_status'] == "Y"

        # S1
        data = {
            "code": "S1",
            "type": "s-semi",
            "desc": None,
            "site_code": "aaa",
            "charge_status": "Y",
            "mill_id": 1,
            "latitude": "2",
            "longitude": "1",
            "updated_at": None,
            "updated_by": None,
            "actions": "Action",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/area", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200
        assert response.json()['code'] == "S1"
        assert response.json()['charge_status'] == "Y"

        # S2
        data = {
            "code": "S2",
            "type": "s-semi",
            "desc": None,
            "site_code": "aaa",
            "charge_status": "Y",
            "mill_id": 1,
            "latitude": "2",
            "longitude": "1",
            "updated_at": None,
            "updated_by": None,
            "actions": "Action",
        }
        response = self.client.post(self.host_url + "/area", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200
        assert response.json()['code'] == "S2"
        assert response.json()['charge_status'] == "Y"

        # T1
        data = {
            "code": "T1",
            "type": "f-finished_product",
            "desc": None,
            "site_code": "aaa",
            "charge_status": "Y",
            "mill_id": 1,
            "latitude": "2",
            "longitude": "1",
            "updated_at": None,
            "updated_by": None,
            "actions": "Action",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/area", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200
        assert response.json()['code'] == "T1"
        assert response.json()['charge_status'] == "Y"
        t1_area_id = response.json()['id']

        # 创建defect reason
        data = {
            "code": "CRS",
            "name": "Crack",
            "type": "semi",
            "desc": None,
            "mill_id": 1,
            "required_roles": "q",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/defect_reason/", json=data, headers=headers)
        assert response.status_code == 200
        # log.debug(response.json())
        assert response.json()['code'] == "CRS"
        assert response.json()['name'] == "Crack"
        assert response.json()['type'] == "semi"

        data = {
            "code": "CRF",
            "name": "Crack",
            "type": "finished",
            "desc": None,
            "mill_id": 1,
            "required_roles": "q",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/defect_reason/", json=data, headers=headers)
        assert response.status_code == 200
        # log.debug(response.json())
        assert response.json()['code'] == "CRF"
        assert response.json()['name'] == "Crack"
        assert response.json()['type'] == "finished"

        # 创建quality
        data = {
            "mill_id": 1,
            "code": "SS330"
        }
        response = self.client.post(self.host_url + "/quality/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "SS330"

        data = {
            "mill_id": 1,
            "code": "SS400"
        }
        response = self.client.post(self.host_url + "/quality/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "SS400"

        # 创建quality_element
        data = {
            "quality_id": 1,
            "type": "Main",
            "is_active": "True",
            "thick_from": "1.00",
            "thick_to": "6.00",
            "main_el_min_value_c": "0.07",
            "main_el_max_value_c": "0.16",
            "main_el_min_value_s": "0.00",
            "main_el_max_value_s": "0.04",
            "main_el_min_value_si": "0.00",
            "main_el_max_value_si": "0.05",
            "main_el_min_value_p": "0.00",
            "main_el_max_value_p": "0.04",
            "main_el_min_value_mn": "0.15",
            "main_el_max_value_mn": "0.55",
            "quality_other_element": []
        }
        response = self.client.post(self.host_url + "/quality_element/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['type'] == "Main"

        data = {
            "quality_id": 2,
            "type": "Main",
            "is_active": "True",
            "thick_from": "6.00",
            "thick_to": "16.00",
            "main_el_min_value_c": "0.08",
            "main_el_max_value_c": "0.17",
            "main_el_min_value_s": "0.00",
            "main_el_max_value_s": "0.04",
            "main_el_min_value_si": "0.00",
            "main_el_max_value_si": "0.06",
            "main_el_min_value_p": "0.00",
            "main_el_max_value_p": "0.04",
            "main_el_min_value_mn": "0.70",
            "main_el_max_value_mn": "1.30",
            "quality_other_element": []
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/quality_element/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['main_el_max_value_si'] == 0.06

        #  创建Semi_size
        data = {
            "mill_id": 1,
            "code": "650-250",
            "semi_type": None,
            "width_mm": 650,
            "thick_mm": 250,
            "norm_suffix": None,
            "id": 1,
            "mill": {
                "id": 1,
                "code": "SCT",
                "type": "SCT",
                "desc": "Mill test"
            },
            "semi_size_detail": None
        }
        response = self.client.post(self.host_url + "/semi_size/", json=data, headers=headers)
        assert response.status_code == 200
        # log.debug(response.json())
        assert response.json()['code'] == "650-250"

        data = {
            "mill_id": 1,
            "code": "700-250",
            "semi_type": None,
            "width_mm": 700,
            "thick_mm": 250,
            "norm_suffix": None,
            "id": 2,
            "mill": {
                "id": 1,
                "code": "SCT",
                "type": "SCT",
            }
        }
        response = self.client.post(self.host_url + "/semi_size/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "700-250"

        data = {
            "mill_id": 1,
            "code": "800-250",
            "semi_type": None,
            "width_mm": 800,
            "thick_mm": 250,
            "norm_suffix": None,
            "id": 3,
            "mill": {
                "id": 1,
                "code": "SCT",
                "type": "SCT",
            }
        }
        response = self.client.post(self.host_url + "/semi_size/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "800-250"


        # 创建cast
        data = {
            "cast_code": "C01",
            "generate_code": "25",
            "bos_cast_code": "6VC01",
            "long_cast_code": "19C01",
            "ch_c": "1.1334",
            "ch_si": "0.185",
            "ch_mn": "1.392",
            "ch_p": "0.0094",
            "ch_s": "0.0196",
            "ch_cr": "1.011",
            "ch_mo": "0.0024",
            "ch_ni": "0.0166",
            "ch_al": "0.037",
            "ch_b": "1.0004",
            "ch_co": "0.008",
            "ch_cu": "0.009",
            "ch_nb": "0.026",
            "ch_sn": "0.002",
            "ch_ti": "0.0005",
            "ch_v": "0.004",
            "ch_n": "0.0055",
            "ch_ca": "0.0001",
            "ch_h": None,
            "ch_as": "0.0024",
            "ch_bi": "0.001",
            "ch_o": None,
            "ch_pb": "0.001",
            "ch_sb": "0.0001",
            "ch_w": "0.0001",
            "ch_te": "0.001",
            "quality_id": 1,
            "quality_code": "SS330"
        }
        response = self.client.post(self.host_url + "/cast/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['cast_code'] == "C01"
        cast_id_c01 = response.json()['id']
        # log.debug(f"cast_id_c01: {cast_id_c01}")

        data = {
            "cast_code": "C02",
            "generate_code": "25",
            "bos_cast_code": "6VC02",
            "long_cast_code": "19C02",
            "ch_c": "0.723",
            "ch_si": "0.311",
            "ch_mn": "0.9752",
            "ch_p": "0.0154",
            "ch_s": "0.018",
            "ch_cr": "0.0135",
            "ch_mo": "0.001",
            "ch_ni": "0.014",
            "ch_al": "0.001",
            "ch_b": "0.003",
            "ch_co": "0.005",
            "ch_cu": "0.0062",
            "ch_nb": "0.001",
            "ch_sn": "0.001",
            "ch_ti": "0.0036",
            "ch_v": "0.0022",
            "ch_n": "0.00291",
            "ch_ca": "0.0001",
            "ch_h": None,
            "ch_as": "0.003",
            "ch_bi": "0.001",
            "ch_o": None,
            "ch_pb": "0.001",
            "ch_sb": "0.0018",
            "ch_w": "0.00061",
            "ch_te": "0.001",
            "quality_id": 2,
            "quality_code": "SS400"
        }
        response = self.client.post(self.host_url + "/cast/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['cast_code'] == "C02"
        cast_id_c02 = response.json()['id']
        # log.debug(f"cast_id_c02: {cast_id_c02}")

        data = {
            "cast_code": "C03",
            "generate_code": "25",
            "bos_cast_code": "6VC03",
            "long_cast_code": "19C03",
            "ch_c": "0.16",
            "ch_si": "0.22",
            "ch_mn": "0.5",
            "ch_p": "0.18",
            "ch_s": "0.012",
            "ch_cr": "0.012",
            "ch_mo": "0.0014",
            "ch_ni": "0.016",
            "ch_al": "0.001",
            "ch_b": "0.0036",
            "ch_co": "0.0058",
            "ch_cu": "0.005",
            "ch_nb": "0.001",
            "ch_sn": "0.001",
            "ch_ti": "0.0001",
            "ch_v": "0.022",
            "ch_n": "0.002",
            "ch_ca": "0.0001",
            "ch_h": None,
            "ch_as": "0.0027",
            "ch_bi": "0.001",
            "ch_o": None,
            "ch_pb": "0.001",
            "ch_sb": "0.0001",
            "ch_w": "0.0011",
            "ch_te": "0.001",
            "quality_id": 2,
            "quality_code": "SS400"
        }
        response = self.client.post(self.host_url + "/cast/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['cast_code'] == "C03"
        cast_id_c03 = response.json()['id']
        # log.debug(f"cast_id_c03: {cast_id_c03}")

        #创建semi
        data = {
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 1,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C01",
            "semi_code": "C01-6B1",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B1",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "650",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "D1",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 1,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "650",
            "dim2": "250",
            "area_": 1
        }
        response = self.client.post(self.host_url + "/semi/", json=data, headers=headers)
        assert response.status_code == 200
        # log.debug(response.json())
        assert response.json()['semi_code'] == "C01-6B1"
        semi_id_c01 = response.json()['id']

        data = {
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 2,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C02",
            "semi_code": "C02-6B1",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B1",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "700",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "S1",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 2,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "700",
            "dim2": "250",
            "area_": 2
        }
        response = self.client.post(self.host_url + "/semi/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['semi_code'] == "C02-6B1"
        semi_id_c02 = response.json()['id']

        data = {
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 3,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C03",
            "semi_code": "C03-6B1",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B1",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "700",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "S2",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 2,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "800",
            "dim2": "250",
            "area_": 3
        }
        response = self.client.post(self.host_url + "/semi/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['semi_code'] == "C03-6B1"
        semi_id_c03 = response.json()['id']

        data = {
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 1,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C01",
            "semi_code": "C01-6B2",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B2",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "650",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "D1",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 1,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "650",
            "dim2": "250",
            "area_": 1
        }
        response = self.client.post(self.host_url + "/semi/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['semi_code'] == "C01-6B2"

        data = {
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 2,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C02",
            "semi_code": "C02-6B2",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B2",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "700",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "S1",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 2,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "700",
            "dim2": "250",
            "area_": 2
        }
        response = self.client.post(self.host_url + "/semi/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['semi_code'] == "C02-6B2"

        data = {
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 3,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C03",
            "semi_code": "C03-6B2",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B2",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "700",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "S2",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 2,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "800",
            "dim2": "250",
            "area_": 3
        }
        response = self.client.post(self.host_url + "/semi/", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['semi_code'] == "C03-6B2"


        # 创建product code
        data = {
            "id": None,
            "code": "HW",
            "mill": None,
            "mill_code": "SCT",
            "type": "1",
            "desc": "1",
            "updated_at": None,
            "updated_by": None,
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/product_class/create", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "HW"

        # 创建product size
        data = {
            "mill_id": 1,
            "code": "HW-200-200-50",
            "type": "1",
            "desc": "1",
            "dim1": "200",
            "dim2": "200",
            "product_code": "HW",
            "product_class_id": 1,
            "product_class_code": "HW",
            "product_category_code": "200-200"
        }
        response = self.client.post(self.host_url + "/product_size/create", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "HW-200-200-50"
        product_size_id_c01 = response.json()['id']
        # log.debug(f"product_size_id_c01: {product_size_id_c01}")

        data = {
            "mill_id": 1,
            "code": "HW-200-255-82",
            "type": "1",
            "desc": "1",
            "dim1": "200",
            "dim2": "255",
            "product_code": "HW",
            "product_class_id": 1,
            "product_class_code": "HW",
            "product_category_code": "200-255"
        }
        response = self.client.post(self.host_url + "/product_size/create", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == "HW-200-255-82"
        product_size_id_c02 = response.json()['id']
        # log.debug(f"product_size_id_c02: {product_size_id_c02}")


        # 创建spec
        data = {
            "mill_id": 1,
            "spec_code": "Q345B",
            "version": 1,
            "version_status": "R",
            "variation_no": 1,
            "full_name": "12345",
            "short_name": "123",
            "summary_name": "Q",
            "alt_spec_code": "Q345B",
            "standard": "1",
            "thick_from": 0,
            "thick_to": 16,
            "dim_f1": 1,
            "dim_f2": 2,
            "dim_f3": 3,
            "dim_f4": 4,
            "dim_b1": 5,
            "dim_b2": 6
        }
        response = self.client.post(self.host_url + "/spec", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['spec_code'] == "Q345B"
        spec_id_q345b = response.json()['id']
        # log.debug(f"spec_id_q345b: {spec_id_q345b}")

        data = {
            "mill_id": 1,
            "spec_code": "Q390A",
            "version": 1,
            "version_status": "R",
            "variation_no": 1,
            "full_name": "12345",
            "short_name": "123",
            "summary_name": "Q",
            "alt_spec_code": "Q390A",

            "thick_from": 0,
            "thick_to": 16,
            "dim_f1": 1,
            "dim_f2": 2,
            "dim_f3": 3,
            "dim_f4": 4,
            "dim_b1": 5,
            "dim_b2": 6
        }
        response = self.client.post(self.host_url + "/spec", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()['spec_code'] == "Q390A"
        spec_id_q390a = response.json()['id']
        # log.debug(f"spec_id_q390a: {spec_id_q390a}")


        #创建spyield
        data = {
            "spec_id": spec_id_q345b,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "yield_min": 295,
            "yield_max": 345,
            "yield_tens_rat_min": 1,
            "yield_tens_rat_max": 1,
            "stress_units": "N",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/spyield", json=data, headers=headers)
        assert response.status_code == 200
        spyield_id_q345b = response.json()['id']
        # log.debug(f"spyield_id_q345b: {spyield_id_q345b}")

        data = {
            "spec_id": spec_id_q390a,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "yield_min": 350,
            "yield_max": 390,
            "yield_tens_rat_min": 1,
            "yield_tens_rat_max": 1,
            "stress_units": "N",
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/spyield", json=data, headers=headers)
        assert response.status_code == 200
        spyield_id_q390a = response.json()['id']
        # log.debug(f"spyield_id_q390a: {spyield_id_q390a}")


        #创建sptensil
        data = {
            "spec_id": spec_id_q345b,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "tensile_min": 470,
            "tensile_max": 630,
            "stress_units": "N",
            "elong_code_1_min": 1,
            "elong_code_2_min": 1,
            "elong_code_3_min": 1,
            "elong_code_4_min": 1,
            "elong_code_5_min": 1,
            "elong_code_6_min": 1,
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/sptensil", json=data, headers=headers)
        assert response.status_code == 200
        sptensil_id_q345b = response.json()['id']
        # log.debug(f"sptensil_id_q345b: {sptensil_id_q345b}")

        data = {
            "spec_id": spec_id_q390a,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "tensile_min": 490,
            "tensile_max": 650,
            "stress_units": "N",
            "elong_code_1_min": 1,
            "elong_code_2_min": 1,
            "elong_code_3_min": 1,
            "elong_code_4_min": 1,
            "elong_code_5_min": 1,
            "elong_code_6_min": 1,
            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/sptensil", json=data, headers=headers)
        assert response.status_code == 200
        sptensil_id_q390a = response.json()['id']
        # log.debug(f"sptensil_id_q390a: {sptensil_id_q390a}")


        #创建spelong
        data = {
            "spec_id": spec_id_q345b,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "elong_min_value": 21,
            "elong_guage_code": "1",

            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/spelong", json=data, headers=headers)
        assert response.status_code == 200
        spelong_id_q345b = response.json()['id']
        # log.debug(f"spelong_id_q345b: {spelong_id_q345b}")

        data = {
            "spec_id": spec_id_q390a,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "elong_min_value": 19,
            "elong_guage_code": "1",

            "flex_form_data": {}
        }
        response = self.client.post(self.host_url + "/spelong", json=data, headers=headers)
        assert response.status_code == 200
        spelong_id_q390a = response.json()['id']
        # log.debug(f"spelong_id_q390a: {spelong_id_q390a}")


        #创建spimpact
        data = {
            "spec_id": spec_id_q345b,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "impact_units": "J",
            "temp_units": "C",
            "ave_value_1": "34",
            "min_value_1": "32",
            "temp_value_1": "20",
            "ave_value_2": "34",
            "min_value_2": "31",
            "temp_value_2": "0",
            "ave_value_3": "34",
            "min_value_3": "30",
            "temp_value_3": "-20",
            "ave_value_4": "27",
            "min_value_4": "25",
            "temp_value_4": "-40",
        }
        response = self.client.post(self.host_url + "/spimpact", json=data, headers=headers)
        assert response.status_code == 200
        spimpact_id_q345b = response.json()['id']
        # log.debug(f"spimpact_id_q345b: {spimpact_id_q345b}")

        data = {
            "spec_id": spec_id_q390a,
            "mill_id": 1,
            "thick_from": 0,
            "thick_to": 16,
            "location": "1",
            "impact_units": "J",
            "temp_units": "C",
            "ave_value_1": "34",
            "min_value_1": "31",
            "temp_value_1": "20",
            "ave_value_2": "34",
            "min_value_2": "32",
            "temp_value_2": "0",
            "ave_value_3": "34",
            "min_value_3": "32",
            "temp_value_3": "-20",
            "ave_value_4": "27",
            "min_value_4": "24",
            "temp_value_4": "-40",
        }
        response = self.client.post(self.host_url + "/spimpact", json=data, headers=headers)
        assert response.status_code == 200
        spimpact_id_q390a = response.json()['id']
        # log.debug(f"spimpact_id_q390a: {spimpact_id_q390a}")

        # 创建specmainel
        data = {
            "spec_id": spec_id_q345b,
            "mill_id": 1,
            "type": "Main",
            "is_active": None,
            "thick_from": 0.0000000000,
            "thick_to": 16.0000000000,
            "location": "T",
            "main_el_min_value_c": 0.2700000000,
            "main_el_max_value_c": 2.3500000000,
            "anal_ind_c": "",
            "opt_ind_c": "",
            "uom_c": None,
            "precision_c": None,
            "main_el_min_value_si": 0.1500000000,
            "main_el_max_value_si": 2.3500000000,
            "anal_ind_si": "",
            "opt_ind_si": "",
            "uom_si": None,
            "precision_si": None,
            "main_el_min_value_mn": 0.0000000000,
            "main_el_max_value_mn": 2.3000000000,
            "anal_ind_mn": "",
            "opt_ind_mn": "",
            "uom_mn": None,
            "precision_mn": None,
            "main_el_min_value_p": 0.0000000000,
            "main_el_max_value_p": 2.0400000000,
            "anal_ind_p": "",
            "opt_ind_p": "",
            "uom_p": None,
            "precision_p": None,
            "main_el_min_value_s": 0.0000000000,
            "main_el_max_value_s": 2.0400000000,
            "anal_ind_s": "",
            "opt_ind_s": "",
            "uom_s": None,
            "precision_s": None,
            "main_el_min_value_cr": 0.4000000000,
            "main_el_max_value_cr": 2.6000000000,
            "anal_ind_cr": "",
            "opt_ind_cr": "M",
            "uom_cr": None,
            "precision_cr": None,
            "main_el_min_value_mo": 0.0000000000,
            "main_el_max_value_mo": 2.0000000000,
            "anal_ind_mo": "",
            "opt_ind_mo": "",
            "uom_mo": None,
            "precision_mo": None,
            "main_el_min_value_ni": 0.0000000000,
            "main_el_max_value_ni": 2.0000000000,
            "anal_ind_ni": "",
            "opt_ind_ni": "",
            "uom_ni": None,
            "precision_ni": None,
            "main_el_min_value_al": 0.0000000000,
            "main_el_max_value_al": 2.0000000000,
            "anal_ind_al": "",
            "opt_ind_al": "",
            "uom_al": None,
            "precision_al": None,
            "main_el_min_value_b": 0.0005000000,
            "main_el_max_value_b": 2.0030000000,
            "anal_ind_b": "",
            "opt_ind_b": "M",
            "uom_b": None,
            "precision_b": None,
            "main_el_min_value_co": 0.0000000000,
            "main_el_max_value_co": 2.0000000000,
            "anal_ind_co": "",
            "opt_ind_co": "",
            "uom_co": None,
            "precision_co": None,
            "main_el_min_value_cu": 0.0000000000,
            "main_el_max_value_cu": 2.0000000000,
            "anal_ind_cu": "",
            "opt_ind_cu": "",
            "uom_cu": None,
            "precision_cu": None,
            "main_el_min_value_nb": 0.0000000000,
            "main_el_max_value_nb": 2.0000000000,
            "anal_ind_nb": "",
            "opt_ind_nb": "",
            "uom_nb": None,
            "precision_nb": None,
            "main_el_min_value_sn": 0.0000000000,
            "main_el_max_value_sn": 2.0000000000,
            "anal_ind_sn": "",
            "opt_ind_sn": "",
            "uom_sn": None,
            "precision_sn": None,
            "main_el_min_value_ti": 0.0000000000,
            "main_el_max_value_ti": 2.0000000000,
            "anal_ind_ti": "",
            "opt_ind_ti": "",
            "uom_ti": None,
            "precision_ti": None,
            "main_el_min_value_v": 0.0000000000,
            "main_el_max_value_v": 2.0000000000,
            "anal_ind_v": "",
            "opt_ind_v": "",
            "uom_v": None,
            "precision_v": None,
            "main_el_min_value_ca": 0.0000000000,
            "main_el_max_value_ca": 2.0000000000,
            "anal_ind_ca": "",
            "opt_ind_ca": "",
            "uom_ca": None,
            "precision_ca": None,
            "main_el_min_value_n": 0.0000000000,
            "main_el_max_value_n": 2.0000000000,
            "anal_ind_n": "",
            "opt_ind_n": "",
            "uom_n": None,
            "precision_n": None,
            "main_el_min_value_h": 0.0000000000,
            "main_el_max_value_h": 2.0000000000,
            "anal_ind_h": "",
            "opt_ind_h": "",
            "uom_h": None,
            "precision_h": None,
            "c_m_ind": "",
            "code_1": "",
            "other_el_min_value_1": 0.0000000000,
            "other_el_max_value_1": 2.0000000000,
            "code_2": "",
            "other_el_min_value_2": 0.0000000000,
            "other_el_max_value_2": 2.0000000000,
            "code_3": "",
            "other_el_min_value_3": 0.0000000000,
            "other_el_max_value_3": 2.0000000000,
            "code_4": "",
            "other_el_min_value_4": 0.0000000000,
            "other_el_max_value_4": 2.0000000000,
            "code_5": "",
            "other_el_min_value_5": 0.0000000000,
            "other_el_max_value_5": 2.0000000000,
            "code_6": "",
            "other_el_min_value_6": 0.0000000000,
            "other_el_max_value_6": 2.0000000000,
            "code_7": "",
            "other_el_min_value_7": 0.0000000000,
            "other_el_max_value_7": 2.0000000000,
            "code_8": "",
            "other_el_min_value_8": 0.0000000000,
            "other_el_max_value_8": 2.0000000000,
            "code_9": "",
            "other_el_min_value_9": 0.0000000000,
            "other_el_max_value_9": 2.0000000000,
            "option_flag": "",
            "other_el_opt_1": "",
            "other_el_opt_2": "",
            "other_el_opt_3": "",
            "other_el_opt_4": "",
            "other_el_opt_5": "",
            "other_el_opt_6": "",
            "other_el_opt_7": "",
            "other_el_opt_8": "",
            "other_el_opt_9": "",
            "filler": "",
            "flex_form_data": {},
            "main_el_min_value_sal": 0.0000000000,
            "main_el_max_value_sal": 2.0000000000,
            "anal_ind_sal": "",
            "opt_ind_sal": "",
            "uom_sal": None,
            "precision_sal": None,
            "main_el_min_value_sp": 0.0000000000,
            "main_el_max_value_sp": 999900.0000000000,
            "anal_ind_sp": "",
            "opt_ind_sp": "",
            "uom_sp": None,
            "precision_sp": None,
            "main_el_min_value_as": 0,
            "main_el_max_value_as": 10,
            "anal_ind_as": None,
            "opt_ind_as": None,
            "uom_as": None,
            "precision_as": None,
            "main_el_min_value_bi": 0,
            "main_el_max_value_bi": 10,
            "anal_ind_bi": None,
            "opt_ind_bi": None,
            "uom_bi": None,
            "precision_bi": None,
            "main_el_min_value_ce": 0,
            "main_el_max_value_ce": 10,
            "anal_ind_ce": None,
            "opt_ind_ce": None,
            "uom_ce": None,
            "precision_ce": None,
            "main_el_min_value_o": 0,
            "main_el_max_value_o": 10,
            "anal_ind_o": None,
            "opt_ind_o": None,
            "uom_o": None,
            "precision_o": None,
            "main_el_min_value_pb": 0,
            "main_el_max_value_pb": 10,
            "anal_ind_pb": None,
            "opt_ind_pb": None,
            "uom_pb": None,
            "precision_pb": None,
            "main_el_min_value_sb": 0,
            "main_el_max_value_sb": 10,
            "anal_ind_sb": None,
            "opt_ind_sb": None,
            "uom_sb": None,
            "precision_sb": None,
            "main_el_min_value_w": 0,
            "main_el_max_value_w": 10,
            "anal_ind_w": None,
            "opt_ind_w": None,
            "uom_w": None,
            "precision_w": None,
            "main_el_min_value_zn": 0,
            "main_el_max_value_zn": 10,
            "anal_ind_zn": None,
            "opt_ind_zn": None,
            "uom_zn": None,
            "precision_zn": None,
            "main_el_min_value_zr": 0,
            "main_el_max_value_zr": 10,
            "anal_ind_zr": None,
            "opt_ind_zr": None,
            "uom_zr": None,
            "precision_zr": None,
            "main_el_min_value_te": 0,
            "main_el_max_value_te": 10,
            "anal_ind_te": None,
            "opt_ind_te": None,
            "uom_te": None,
            "precision_te": None,
            "main_el_min_value_rad": 0,
            "main_el_max_value_rad": 10,
            "anal_ind_rad": None,
            "opt_ind_rad": None,
            "uom_rad": None,
            "precision_rad": None,
            "main_el_min_value_insal": 0,
            "main_el_max_value_insal": 10,
            "anal_ind_insal": None,
            "opt_ind_insal": None,
            "uom_insal": None,
            "precision_insal": None,
            "main_el_min_value_n2": 0,
            "main_el_max_value_n2": 10,
            "anal_ind_n2": None,
            "opt_ind_n2": None,
            "uom_n2": None,
            "precision_n2": None
        }
        response = self.client.post(self.host_url + "/spmainel", json=data, headers=headers)
        assert response.status_code == 200
        spmainel_id_q345b = response.json()['id']
        # log.debug(f"spmainel_id_q345b: {spmainel_id_q345b}")

        data = {
            "spec_id": spec_id_q390a,
            "mill_id": 1,
            "type": "Main",
            "is_active": None,
            "thick_from": 0.0000000000,
            "thick_to": 16.0000000000,
            "location": "T",
            "main_el_min_value_c": 0.2700000000,
            "main_el_max_value_c": 2.3500000000,
            "anal_ind_c": "",
            "opt_ind_c": "",
            "uom_c": None,
            "precision_c": None,
            "main_el_min_value_si": 0.1500000000,
            "main_el_max_value_si": 2.3500000000,
            "anal_ind_si": "",
            "opt_ind_si": "",
            "uom_si": None,
            "precision_si": None,
            "main_el_min_value_mn": 0.0000000000,
            "main_el_max_value_mn": 2.3000000000,
            "anal_ind_mn": "",
            "opt_ind_mn": "",
            "uom_mn": None,
            "precision_mn": None,
            "main_el_min_value_p": 0.0000000000,
            "main_el_max_value_p": 2.0400000000,
            "anal_ind_p": "",
            "opt_ind_p": "",
            "uom_p": None,
            "precision_p": None,
            "main_el_min_value_s": 0.0000000000,
            "main_el_max_value_s": 2.0400000000,
            "anal_ind_s": "",
            "opt_ind_s": "",
            "uom_s": None,
            "precision_s": None,
            "main_el_min_value_cr": 0.4000000000,
            "main_el_max_value_cr": 2.6000000000,
            "anal_ind_cr": "",
            "opt_ind_cr": "M",
            "uom_cr": None,
            "precision_cr": None,
            "main_el_min_value_mo": 0.0000000000,
            "main_el_max_value_mo": 2.0000000000,
            "anal_ind_mo": "",
            "opt_ind_mo": "",
            "uom_mo": None,
            "precision_mo": None,
            "main_el_min_value_ni": 0.0000000000,
            "main_el_max_value_ni": 2.0000000000,
            "anal_ind_ni": "",
            "opt_ind_ni": "",
            "uom_ni": None,
            "precision_ni": None,
            "main_el_min_value_al": 0.0000000000,
            "main_el_max_value_al": 2.0000000000,
            "anal_ind_al": "",
            "opt_ind_al": "",
            "uom_al": None,
            "precision_al": None,
            "main_el_min_value_b": 0.0005000000,
            "main_el_max_value_b": 2.0030000000,
            "anal_ind_b": "",
            "opt_ind_b": "M",
            "uom_b": None,
            "precision_b": None,
            "main_el_min_value_co": 0.0000000000,
            "main_el_max_value_co": 2.0000000000,
            "anal_ind_co": "",
            "opt_ind_co": "",
            "uom_co": None,
            "precision_co": None,
            "main_el_min_value_cu": 0.0000000000,
            "main_el_max_value_cu": 2.0000000000,
            "anal_ind_cu": "",
            "opt_ind_cu": "",
            "uom_cu": None,
            "precision_cu": None,
            "main_el_min_value_nb": 0.0000000000,
            "main_el_max_value_nb": 2.0000000000,
            "anal_ind_nb": "",
            "opt_ind_nb": "",
            "uom_nb": None,
            "precision_nb": None,
            "main_el_min_value_sn": 0.0000000000,
            "main_el_max_value_sn": 2.0000000000,
            "anal_ind_sn": "",
            "opt_ind_sn": "",
            "uom_sn": None,
            "precision_sn": None,
            "main_el_min_value_ti": 0.0000000000,
            "main_el_max_value_ti": 2.0000000000,
            "anal_ind_ti": "",
            "opt_ind_ti": "",
            "uom_ti": None,
            "precision_ti": None,
            "main_el_min_value_v": 0.0000000000,
            "main_el_max_value_v": 2.0000000000,
            "anal_ind_v": "",
            "opt_ind_v": "",
            "uom_v": None,
            "precision_v": None,
            "main_el_min_value_ca": 0.0000000000,
            "main_el_max_value_ca": 2.0000000000,
            "anal_ind_ca": "",
            "opt_ind_ca": "",
            "uom_ca": None,
            "precision_ca": None,
            "main_el_min_value_n": 0.0000000000,
            "main_el_max_value_n": 2.0000000000,
            "anal_ind_n": "",
            "opt_ind_n": "",
            "uom_n": None,
            "precision_n": None,
            "main_el_min_value_h": 0.0000000000,
            "main_el_max_value_h": 2.0000000000,
            "anal_ind_h": "",
            "opt_ind_h": "",
            "uom_h": None,
            "precision_h": None,
            "c_m_ind": "",
            "code_1": "",
            "other_el_min_value_1": 0.0000000000,
            "other_el_max_value_1": 2.0000000000,
            "code_2": "",
            "other_el_min_value_2": 0.0000000000,
            "other_el_max_value_2": 2.0000000000,
            "code_3": "",
            "other_el_min_value_3": 0.0000000000,
            "other_el_max_value_3": 2.0000000000,
            "code_4": "",
            "other_el_min_value_4": 0.0000000000,
            "other_el_max_value_4": 2.0000000000,
            "code_5": "",
            "other_el_min_value_5": 0.0000000000,
            "other_el_max_value_5": 2.0000000000,
            "code_6": "",
            "other_el_min_value_6": 0.0000000000,
            "other_el_max_value_6": 2.0000000000,
            "code_7": "",
            "other_el_min_value_7": 0.0000000000,
            "other_el_max_value_7": 2.0000000000,
            "code_8": "",
            "other_el_min_value_8": 0.0000000000,
            "other_el_max_value_8": 2.0000000000,
            "code_9": "",
            "other_el_min_value_9": 0.0000000000,
            "other_el_max_value_9": 2.0000000000,
            "option_flag": "",
            "other_el_opt_1": "",
            "other_el_opt_2": "",
            "other_el_opt_3": "",
            "other_el_opt_4": "",
            "other_el_opt_5": "",
            "other_el_opt_6": "",
            "other_el_opt_7": "",
            "other_el_opt_8": "",
            "other_el_opt_9": "",
            "filler": "",
            "flex_form_data": {},
            "main_el_min_value_sal": 0.0000000000,
            "main_el_max_value_sal": 2.0000000000,
            "anal_ind_sal": "",
            "opt_ind_sal": "",
            "uom_sal": None,
            "precision_sal": None,
            "main_el_min_value_sp": 0.0000000000,
            "main_el_max_value_sp": 999900.0000000000,
            "anal_ind_sp": "",
            "opt_ind_sp": "",
            "uom_sp": None,
            "precision_sp": None,
            "main_el_min_value_as": 0,
            "main_el_max_value_as": 10,
            "anal_ind_as": None,
            "opt_ind_as": None,
            "uom_as": None,
            "precision_as": None,
            "main_el_min_value_bi": 0,
            "main_el_max_value_bi": 10,
            "anal_ind_bi": None,
            "opt_ind_bi": None,
            "uom_bi": None,
            "precision_bi": None,
            "main_el_min_value_ce": 0,
            "main_el_max_value_ce": 10,
            "anal_ind_ce": None,
            "opt_ind_ce": None,
            "uom_ce": None,
            "precision_ce": None,
            "main_el_min_value_o": 0,
            "main_el_max_value_o": 10,
            "anal_ind_o": None,
            "opt_ind_o": None,
            "uom_o": None,
            "precision_o": None,
            "main_el_min_value_pb": 0,
            "main_el_max_value_pb": 10,
            "anal_ind_pb": None,
            "opt_ind_pb": None,
            "uom_pb": None,
            "precision_pb": None,
            "main_el_min_value_sb": 0,
            "main_el_max_value_sb": 10,
            "anal_ind_sb": None,
            "opt_ind_sb": None,
            "uom_sb": None,
            "precision_sb": None,
            "main_el_min_value_w": 0,
            "main_el_max_value_w": 10,
            "anal_ind_w": None,
            "opt_ind_w": None,
            "uom_w": None,
            "precision_w": None,
            "main_el_min_value_zn": 0,
            "main_el_max_value_zn": 10,
            "anal_ind_zn": None,
            "opt_ind_zn": None,
            "uom_zn": None,
            "precision_zn": None,
            "main_el_min_value_zr": 0,
            "main_el_max_value_zr": 10,
            "anal_ind_zr": None,
            "opt_ind_zr": None,
            "uom_zr": None,
            "precision_zr": None,
            "main_el_min_value_te": 0,
            "main_el_max_value_te": 10,
            "anal_ind_te": None,
            "opt_ind_te": None,
            "uom_te": None,
            "precision_te": None,
            "main_el_min_value_rad": 0,
            "main_el_max_value_rad": 10,
            "anal_ind_rad": None,
            "opt_ind_rad": None,
            "uom_rad": None,
            "precision_rad": None,
            "main_el_min_value_insal": 0,
            "main_el_max_value_insal": 10,
            "anal_ind_insal": None,
            "opt_ind_insal": None,
            "uom_insal": None,
            "precision_insal": None,
            "main_el_min_value_n2": 0,
            "main_el_max_value_n2": 10,
            "anal_ind_n2": None,
            "opt_ind_n2": None,
            "uom_n2": None,
            "precision_n2": None
        }
        response = self.client.post(self.host_url + "/spmainel", json=data, headers=headers)
        assert response.status_code == 200
        spmainel_id_q390a = response.json()['id']
        # log.debug(f"spmainel_id_q390a: {spmainel_id_q390a}")


        #模拟51消息，更新semi状态
        data = {
            "location": "COGG",
            "semi_status": "DROPOUT",
            "furnace_sequence_number": "709"
        }
        response = self.client.put(self.host_url + f"/semi/{semi_id_c01}", json=data, headers=headers)
        assert response.status_code == 200

        #get by code
        response = self.client.get(self.host_url + f"/semi/semi_code/C01-6B1", headers=headers)
        assert response.status_code == 200
        assert response.json()['location'] == 'COGG'
        assert response.json()['semi_status'] == 'DROPOUT'
        assert response.json()['furnace_sequence_number'] == '709'

        data = {
            "location": "COGG",
            "semi_status": "DROPOUT",
            "furnace_sequence_number": "916"
        }
        response = self.client.put(self.host_url + f"/semi/{semi_id_c02}", json=data, headers=headers)
        assert response.status_code == 200

        #get by code
        response = self.client.get(self.host_url + f"/semi/semi_code/C02-6B1", headers=headers)
        assert response.status_code == 200
        assert response.json()['location'] == 'COGG'
        assert response.json()['semi_status'] == 'DROPOUT'
        assert response.json()['furnace_sequence_number'] == '916'

        #创建product category
        data = {
            "mill_id": 1,
            "code": "HW-200-200",
            "mill_code": "SCT",
            "dim1": 200,
            "dim2": 200,
            "dim3": None,
            "dim4": None,
        }
        response = self.client.post(self.host_url + f"/product_category/create", json=data, headers=headers)
        assert response.status_code == 200
        product_category_id_c01 = response.json()['id']
        # log.debug(f"product_category_id_c01: {product_category_id_c01}")

        data = {
            "mill_id": 1,
            "code": "HW-200-255",
            "mill_code": "SCT",
            "dim1": 200,
            "dim2": 255,
            "dim3": None,
            "dim4": None,
        }
        response = self.client.post(self.host_url + f"/product_category/create", json=data, headers=headers)
        assert response.status_code == 200
        product_category_id_c02 = response.json()['id']
        # log.debug(f"product_category_id_c02: {product_category_id_c02}")


        #创建product type
        data = {
            "mill_id": 1,
            "product_category_id": product_category_id_c01,
            "product_category_code": '200-200',
            "product_class_code": 'HW',
            "tolerance_code": "123",
            "code": "HW-200-200-50",
            "mill_code": "SCT",
            "dim1": 200,
            "dim2": 200,
            "dim3": 50,
            "dim4": None,
            "flange_thickness": 12,
        }
        response = self.client.post(self.host_url + f"/product_type/create", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200
        product_type_id_c01 = response.json()['product_type']['id']
        # log.debug(f"product_type_id_c01: {product_type_id_c01}")

        data = {
            "mill_id": 1,
            "product_category_id": product_category_id_c02,
            "product_category_code": '200-255',
            "product_class_code": 'HW',
            "tolerance_code": "123",
            "code": "HW-200-255-82",
            "mill_code": "SCT",
            "dim1": 200,
            "dim2": 255,
            "dim3": 82,
            "dim4": None,
            "flange_thickness": 14,
        }
        response = self.client.post(self.host_url + f"/product_type/create", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200
        product_type_id_c02 = response.json()['product_type']['id']
        # log.debug(f"product_type_id_c02: {product_type_id_c02}")

        # create alternative semi size
        data = {
            "mill_id": 1,
            "product_type_id": product_type_id_c01,
            "semi_size_id": 1,
            "semi_width": 650,
            "thickness": 250,
            "opt_length": 7900,
            "weight": None,
            "max_length": None,
            "min_length": None,
            "rank_seq": "100"
        }
        response = self.client.post(self.host_url + f"/alternative_semi_size/", json=data, headers=headers)
        assert response.status_code == 200

        data = {
            "mill_id": 1,
            "product_type_id": product_type_id_c02,
            "semi_size_id": 2,
            "semi_width": 700,
            "thickness": 250,
            "opt_length": 7900,
            "weight": None,
            "max_length": None,
            "min_length": None,
            "rank_seq": "100"
        }
        response = self.client.post(self.host_url + f"/alternative_semi_size/", json=data, headers=headers)
        assert response.status_code == 200

        data = {
            "mill_id": 1,
            "product_type_id": product_type_id_c02,
            "semi_size_id": 3,
            "semi_width": 800,
            "thickness": 250,
            "opt_length": 7900,
            "weight": None,
            "max_length": None,
            "min_length": None,
            "rank_seq": "100"
        }
        response = self.client.post(self.host_url + f"/alternative_semi_size/", json=data, headers=headers)
        assert response.status_code == 200

        # create rolling(SCT)
        data = {
            "rolling_code": "HW-200-200-A01",
            "programmed_start_date": "2025-05-01",
            "duration_minutes": 12,
            "programmed_tonnage": 200,

            "short_code": "A01",
            "rolling_dim1": "200",
            "rolling_dim2": "200",
            "mill_code": "SCT",
            "mill_id": 1,
            "product_size_id": 1,
            "rolling_status": "Open",
            "rolling_time_total": 0,
            "quantity": 20,
            "week_number": "1",
            "rolling_seq": 1
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/rolling", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200

        data = {
            "mill_code": "SCT",
            "mill_id": 1,
            "rolling_code": "HW-200-255-B01",
            "product_size_id": 2,  # 需已有 product_size 数据并获取其 id
            "rolling_dim1": "200",
            "rolling_dim2": "255",
            "short_code": "B01",
            "rolling_status": "Open",  # 示例状态
            "rolling_time_total": 0,
            "programmed_start_date": "2025-05-02",
            "duration_minutes": 30,
            "quantity": 20,
            "week_number": "18",  # 2025年5月2日为第18周
            "rolling_seq": 2
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/rolling", json=data, headers=headers)
        # log.debug(response.json())
        assert response.status_code == 200

        data = {
            "order_code": "Order1",
            "sap_order_code": "SOrder1",
            "type_of_order": 1,
            "address_line_1": "1234 Elmwood Drive, Apt 5B, Springfield, IL 62704, UK"
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/order", json=data, headers=headers)
        assert response.status_code == 200

        data = {
            "order_code": "Order2",
            "sap_order_code": "SOrder2",
            "type_of_order": 1,
            "address_line_1": "1235 Elmwood Drive, Apt 6B, Springfield, IL 62700, UK"
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/order", json=data, headers=headers)
        assert response.status_code == 200


        data = {
            "order_id": 1,
            "rolling_code": "HW-200-200-A01",
            "rolling_id": 1,
            "plant_id": 1,
            "product_type_id": product_type_id_c01,
            "line_item_code": "000001",
            "spec_code": "Q345B",
            "spec_id": 1,
            "quantity": 20,
            "quality_code": "SS330",
            "stocked_quantity": 20,
            "tonnage": 50
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/order_item", json=data, headers=headers)
        assert response.status_code == 200

        data = {
            "order_id": 2,
            "rolling_code": "HW-200-255-B01",
            "rolling_id": 2,
            "plant_id": 1,
            "product_type_id": product_type_id_c02,
            "line_item_code": "000002",
            "spec_code": "Q390A",
            "spec_id": 2,
            "quantity": 20,
            "quality_code": "SS400",
            "stocked_quantity": 20,
            "tonnage": 50
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/order_item", json=data, headers=headers)
        assert response.status_code == 200


        #创建runout
        data = {
            "runout_code": "999998",
            "mill_id": 1,
            "cast_id":cast_id_c01,
            "product_type_id": product_type_id_c01
        }
        response = self.client.post(self.host_url + f"/runout/", json=data, headers=headers)
        assert response.status_code == 200
        runout_id = response.json()['id']
        # log.debug(f"runout_id: {runout_id}")

        #创建finished product
        data = {
            "code": "999998A",
            "order_id": 1,
            "order_item_id": 1,
            "runout_id": runout_id,
            "product_type_id": product_type_id_c01,
            "type": "bar",
            "length_mm": 18300,
            "estimated_weight_kg": 4300,
            "mill_id": 1,
            "quantity": 1,
            "status": "created",
            "spec_id": spec_id_q345b,
            "cast_id": cast_id_c01,
            "quality_code": "1",
            "thickness_mm": "12",
            "exist_flag": "Y",
        }
        response = self.client.post(self.host_url + "/finished_product/", json=data, headers=headers)
        assert response.status_code == 200
        finished_product_id_1 = response.json()['id']
        # log.debug(f"finished_product_id_1: {finished_product_id_1}")

        response = self.client.get(self.host_url + f"/finished_product/{finished_product_id_1}", headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == '999998A'
        assert response.json()['length_mm'] == 18300.0
        assert response.json()['estimated_weight_kg'] == 4300.0

        data = {
            "code": "999998B",
            "order_id": 1,
            "order_item_id": 1,
            "runout_id": runout_id,
            "product_type_id": product_type_id_c01,
            "type": "bar",
            "length_mm": 16000,
            "estimated_weight_kg": 1620,
            "mill_id": 1,
            "quantity": 3,
            "status": "created",
            "spec_id": spec_id_q345b,
            "cast_id": cast_id_c01,
            "quality_code": "1",
            "thickness_mm": "12",
            "exist_flag": "Y",
        }
        response = self.client.post(self.host_url + "/finished_product/", json=data, headers=headers)
        assert response.status_code == 200
        finished_product_id_2 = response.json()['id']
        # log.debug(f"finished_product_id_2: {finished_product_id_2}")

        response = self.client.get(self.host_url + f"/finished_product/{finished_product_id_2}", headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == '999998B'
        assert response.json()['length_mm'] == 16000.0
        assert response.json()['estimated_weight_kg'] == 1620.0

        data = {
            "code": "999998C",
            "order_id": 2,
            "order_item_id": 2,
            "runout_id": runout_id,
            "product_type_id": product_type_id_c01,
            "type": "bar",
            "length_mm": 13500,
            "estimated_weight_kg": 2720,
            "mill_id": 1,
            "quantity": 6,
            "status": "created",
            "spec_id": spec_id_q345b,
            "cast_id": cast_id_c01,
            "quality_code": "1",
            "thickness_mm": "12",
            "exist_flag": "Y",
        }
        response = self.client.post(self.host_url + "/finished_product/", json=data, headers=headers)
        assert response.status_code == 200
        finished_product_id_3 = response.json()['id']
        # log.debug(f"finished_product_id_3: {finished_product_id_3}")

        response = self.client.get(self.host_url + f"/finished_product/{finished_product_id_3}", headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == '999998C'
        assert response.json()['length_mm'] == 13500.0
        assert response.json()['estimated_weight_kg'] == 2720.0

        data = {
            "code": "999998D",
            "order_id": 2,
            "order_item_id": 2,
            "runout_id": runout_id,
            "product_type_id": product_type_id_c02,
            "type": "bar",
            "length_mm": 15500,
            "estimated_weight_kg": 3320,
            "mill_id": 1,
            "quantity": 4,
            "status": "created",
            "spec_id": spec_id_q390a,
            "cast_id": cast_id_c02,
            "quality_code": "1",
            "thickness_mm": "14",
            "exist_flag": "Y",
        }
        response = self.client.post(self.host_url + "/finished_product/", json=data, headers=headers)
        assert response.status_code == 200
        finished_product_id_4 = response.json()['id']
        # log.debug(f"finished_product_id_4: {finished_product_id_4}")

        response = self.client.get(self.host_url + f"/finished_product/{finished_product_id_4}", headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == '999998D'
        assert response.json()['length_mm'] == 15500.0
        assert response.json()['estimated_weight_kg'] == 3320.0

        data = {
            "code": "999998E",
            "order_id": 2,
            "order_item_id": 2,
            "runout_id": runout_id,
            "product_type_id": product_type_id_c02,
            "type": "bar",
            "length_mm": 14300,
            "estimated_weight_kg": 1830,
            "mill_id": 1,
            "quantity": 2,
            "status": "created",
            "spec_id": spec_id_q390a,
            "cast_id": cast_id_c02,
            "quality_code": "1",
            "thickness_mm": "14",
            "exist_flag": "Y",
        }
        response = self.client.post(self.host_url + "/finished_product/", json=data, headers=headers)
        assert response.status_code == 200
        finished_product_id_5 = response.json()['id']
        # log.debug(f"finished_product_id_5: {finished_product_id_5}")

        response = self.client.get(self.host_url + f"/finished_product/{finished_product_id_5}", headers=headers)
        assert response.status_code == 200
        assert response.json()['code'] == '999998E'
        assert response.json()['length_mm'] == 14300.0
        assert response.json()['estimated_weight_kg'] == 1830.0

        """
            advice pytest
        """

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}

        data = {
            "type": "transfer",
            "business_type": "internal",
            "customer": "BARRETT STEEL LIMITED",
            "transport_type": "T1",
            # "transport_id": 1,
            "haulier": "123",
            # "load_id": 1001,
            "destination": "BS TEES Quanrantine Benches",
            "total_no_bars": 3,
            "total_weight": 2847,
            "max_length": 14000,
            "order_id": 1,
            "consignee": "Consignee Test",
            "comment": "test new advice ",
            "is_load_status": False,
            # "shift_id": 3,
            "port": "Port Test",
            "finished_ids": [
                finished_product_id_4,
                finished_product_id_5
            ]
        }
        response = self.client.post(self.host_url + "/advice/", json=data, headers=headers)
        # global advice_id
        assert response.status_code == 200
        OverAllAPI.advice_id = response.json().get("id", None)
        OverAllAPI.advice_code = response.json().get("advice_code", None)

        assert OverAllAPI.advice_id is not None
        data = {
            "advice_ids": [
                OverAllAPI.advice_id
            ]
        }
        # headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + f"/advice/finished", json=data, headers=headers)
        assert response.status_code == 200

        data = {
            "advice_codes": [
                f"{OverAllAPI.advice_code}"
            ],
            "area_id": t1_area_id,
            "comment": "test advice tipped",
            "business_type": "internal",
            "advice_ids": [
                OverAllAPI.advice_id
            ]
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.put(
            self.host_url + f"/advice/tip_update", json=data, headers=headers
        )
        assert response.status_code == 200

        url = f"{self.host_url}/advice/tip/{OverAllAPI.advice_id}"
        response = self.client.get(url, headers=headers)
        assert response.status_code == 200 or response.status_code == 400, f"Expected status code 200, but got {response.status_code}"

        url = f"{self.host_url}/message_server/push_message/sap_900_auth"
        headers["Content-Type"] = "application/xml"
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
            <MovementDetails>
                <SSRC>801TBR</SSRC>
                <Werks>TBM</Werks>
                <Action>RELEASE</Action>
                <MVDate>05.08.2024</MVDate>
                <ConNo>C34566</ConNo>
                <NoOfLines>2</NoOfLines>
                <PieceDetails>
                    <Batch>
                        <BatchID>999998D</BatchID>
                        <BatchType>PCE</BatchType>
                        <Pieces>0001</Pieces>
                    </Batch>
                </PieceDetails>
            </MovementDetails>
        """
        response = self.client.post(url, headers=headers, data=xml_data)
        assert response.status_code == 200
        # finished_product_ids = dict(response.json()).get("batch_ids", None)
        # log.debug(f"finished_product_ids: {finished_product_ids}")
        # for finished_product_id in finished_product_ids:
        #     headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        #     # response = self.client.get(self.host_url + f"/finished_product/{finished_product_id}", headers=headers)
        #     response = self.client.get(self.host_url + f"/finished_product/?q=&page=1&itemsPerPage=10&fields[]=code&ops[]=eq&values[]={finished_product_id}", headers=headers)
        #     log.debug(f"finished_product_id: {response.json()}")
        #     assert response.status_code == 200
        #     assert response.json()["items"][0]["status"] == "despatched"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.get(self.host_url + f"/finished_product/{finished_product_id_4}", headers=headers)
        log.debug(f"finished_product_id: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "despatched"
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        data = {
            "id": 1,
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/rolling/allocate_blocks", json=data, headers=headers)
        response_1 = self.client.get(self.host_url + "/order_group/", headers=headers)
        log.debug(response_1.json())
        assert response.status_code == 200

        data = [{
            "id": 1,
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 1,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C01",
            "semi_code": "C01-6B1",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B1",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "650",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": 1,
            "curren_allocated_block": None,
            "area_code": "D1",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 1,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "250",
            "dim2": "650",
            "area_": 1,
            "order_group_id": 1
            ,
        }, {
            "id": 4,
            "rolling": None,
            "site": None,
            "site_id": None,
            "area_id": 1,
            "semi_load_code": None,
            "semi_charge_seq": "2",
            "cast_code": "C01",
            "semi_code": "C01-6B2",
            "location": None,
            "stock_in_date": None,
            "skelp_code": "6B2",
            "semi_cut_seq": "2",
            "semi_code_1": None,
            "product_type": None,
            "quantity": None,
            "quality_code": None,
            "length_mm": "650",
            "width_mm": "250",
            "thickness_mm": None,
            "estimated_weight_kg": "50",
            "scarfed_status": None,
            "curren_allocated_rolling": None,
            "curren_allocated_block": None,
            "area_code": "D1",
            "updated_at": None,
            "updated_by": None,
            "created_at": None,
            "created_by": None,
            "is_deleted": None,
            "flex_form_data": {},
            "semi_type": "Bloom",
            "hold_reason": None,
            "comment": None,
            "cast_id": None,
            "defect_reason": None,
            "quality_id": 1,
            "quality": None,
            "long_semi_code": None,
            "generate_code": None,
            "semi_status": "Created",
            "dim1": "650",
            "dim2": "250",
            "area_": 1,
            "order_group_id": 1
        }]
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/semi/block", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        data = {
            "runout_code": '888898',
            "mill_id": 1,
            "rolling_id": 1,
            "cast_id": 1
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/runout", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        data = {
            "test_sample_code": '8888981',
            "mill_id": 1,
            "runout_id": 2,
            "cast_id": 1
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/test_sample", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        data = {
            "runout_code": '888899',
            "mill_id": 1,
            "rolling_id": 1,
            "cast_id": 2
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/runout", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        data = {
            "test_sample_code": '8888991',
            "mill_id": 1,
            "runout_id": 3,
            "cast_id": 2
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/test_sample", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        data = {
            "test_code": "000001",
            "mf_test_code": "000001",
            "mill_id": 1,
            "runout_id": 1,
            "test_sample_id": 1,
            "type": "tensile",
            "spec_id": 1,
            "sub_test_in": 
            {
                'tested_thickness': 7.37,
                'tested_width': 23.48,
                'tested_diameter': 0,
                'yield_tt0_5': 402,
                'yield_rp0_2': 401,
                'yield_low': 401,
                'yield_': 415,
                'elongation_code': '2',
                'elongation': 21.2,
                'elongation_a565': 0,
                'area': 173.05,
                'test_standard': 1,
                'retest_seq': 0,
                'value_mpa': 555
            }
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/test/new/create", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        data = {
            "test_code": "000002",
            "mf_test_code": "000002",
            "mill_id": 1,
            "runout_id": 1,
            "test_sample_id": 1,
            "type": "impact",
            "spec_id": 1,
            "sub_test_in": 
            {
                'retest_seq': 0,
                'testing_machine': '05',
                'energy_1_j': 44.0,
                'energy_2_j': 51.0,
                'energy_3_j': 42.0,
                'energy_average_j': 46,
                'standard': '1',
                'temp_c': 0
            }
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.post(self.host_url + "/test/new/create", json=data, headers=headers)
        log.debug(response.json())
        assert response.status_code == 200

        '''
        CAST END USE
        '''

        # cast run_end_use
        response = self.client.post(
            self.host_url + f"/cast_spec/run_end_use_sct/{cast_id_c01}",headers=self.headers,json={},
        )
        assert response.status_code == 200
        response = self.client.post(
            self.host_url + f"/cast_spec/run_end_use_sct/{cast_id_c02}",headers=self.headers,json={},
        )
        assert response.status_code == 200
        response = self.client.post(
            self.host_url + f"/cast_spec/run_end_use_sct/{cast_id_c03}",headers=self.headers,json={},
        )
        assert response.status_code == 200

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.get(self.host_url + f"/cast_spec/cast_spec_list/{cast_id_c01}", headers=headers)
        data = response.json()
        log.debug(data)
        assert any(item["spec"]["spec_code"] in ("Q345B", "Q390A") for item in data["items"])
        assert response.status_code == 200

        '''
        COVERING 
        '''

        #创建test sample
        data = {
            "runout_id":runout_id,
            "test_sample_code":"test1",
            "test_sample_part":"F",
            "mill_id": 1,
            "cast_id":cast_id_c01,
            "concast_code":'C01',
            "sample_thickness":10,
            "retest":'0',
            "standard":'BSEN'
        }
        response = self.client.post(self.host_url + "/test_sample/", json=data, headers=headers)
        assert response.status_code == 200
        test_sample_id_1 = response.json()['id']

        data = {
            "runout_id":runout_id,
            "test_sample_code":"test2",
            "test_sample_part":"F",
            "mill_id": 1,
            "cast_id":cast_id_c01,
            "concast_code":'C01',
            "sample_thickness":10,
            "retest":'0',
            "standard":'BSEN'
        }
        response = self.client.post(self.host_url + "/test_sample/", json=data, headers=headers)
        assert response.status_code == 200
        test_sample_id_2 = response.json()['id']

        data = {
            "runout_id":runout_id,
            "test_sample_code":"test3",
            "test_sample_part":"F",
            "mill_id": 1,
            "cast_id":cast_id_c01,
            "concast_code":'C01',
            "sample_thickness":10,
            "retest":'0',
            "standard":'BSEN'
        }
        response = self.client.post(self.host_url + "/test_sample/", json=data, headers=headers)
        assert response.status_code == 200
        test_sample_id_3 = response.json()['id']

        data = {
            "runout_id":runout_id,
            "test_sample_code":"test4",
            "test_sample_part":"F",
            "mill_id": 1,
            "cast_id":cast_id_c01,
            "concast_code":'C01',
            "sample_thickness":10,
            "retest":'0',
            "standard":'BSEN'
        }
        response = self.client.post(self.host_url + "/test_sample/", json=data, headers=headers)
        assert response.status_code == 200
        test_sample_id_4 = response.json()['id']

        data = {
            "runout_id":runout_id,
            "test_sample_code":"test5",
            "test_sample_part":"F",
            "mill_id": 1,
            "cast_id":cast_id_c01,
            "concast_code":'C01',
            "sample_thickness":10,
            "retest":'0',
            "standard":'BSEN'
        }
        response = self.client.post(self.host_url + "/test_sample/", json=data, headers=headers)
        assert response.status_code == 200
        test_sample_id_5 = response.json()['id']

        # 创建test
        data = {
            "cast_id":cast_id_c01,
            "mill_id": 1,
            "test_code":"tensile1",
            "test_sample_id":test_sample_id_1,
            "runout_id":runout_id,
            "type":'tensile',
            "print_status":'Not Printed',
            "tensile":0,
            "bend":0,
            "impact":0,
            "hardness":0,
            "resistivity":0,
            "cleanness":0,
            "decarburisation":0,
            "sulphur":0,
            "hydrogen":0,
            "prodan":0,
        }
        response = self.client.post(self.host_url + "/test/", json=data, headers=headers)
        assert response.status_code == 200
        test_id_1 = response.json()['id']

        data = {
            "cast_id":cast_id_c01,
            "mill_id": 1,
            "test_code":"impact1",
            "test_sample_id":test_sample_id_2,
            "runout_id":runout_id,
            "type":'impact',
            "print_status":'Not Printed',
            "tensile":0,
            "bend":0,
            "impact":0,
            "hardness":0,
            "resistivity":0,
            "cleanness":0,
            "decarburisation":0,
            "sulphur":0,
            "hydrogen":0,
            "prodan":0,
        }
        response = self.client.post(self.host_url + "/test/", json=data, headers=headers)
        assert response.status_code == 200
        test_id_2 = response.json()['id']

        data = {
            "cast_id":cast_id_c01,
            "mill_id": 1,
            "test_code":"impact2",
            "test_sample_id":test_sample_id_3,
            "runout_id":runout_id,
            "type":'impact',
            "print_status":'Not Printed',
            "tensile":0,
            "bend":0,
            "impact":0,
            "hardness":0,
            "resistivity":0,
            "cleanness":0,
            "decarburisation":0,
            "sulphur":0,
            "hydrogen":0,
            "prodan":0,
        }
        response = self.client.post(self.host_url + "/test/", json=data, headers=headers)
        assert response.status_code == 200
        test_id_3 = response.json()['id']


        data = {
            "cast_id":cast_id_c01,
            "mill_id": 1,
            "test_code":"impact3",
            "test_sample_id":test_sample_id_4,
            "runout_id":runout_id,
            "type":'impact',
            "print_status":'Not Printed',
            "tensile":0,
            "bend":0,
            "impact":0,
            "hardness":0,
            "resistivity":0,
            "cleanness":0,
            "decarburisation":0,
            "sulphur":0,
            "hydrogen":0,
            "prodan":0,
        }
        response = self.client.post(self.host_url + "/test/", json=data, headers=headers)
        assert response.status_code == 200
        test_id_4 = response.json()['id']

        data = {
            "cast_id":cast_id_c01,
            "mill_id": 1,
            "test_code":"impact4",
            "test_sample_id":test_sample_id_5,
            "runout_id":runout_id,
            "type":'impact',
            "print_status":'Not Printed',
            "tensile":0,
            "bend":0,
            "impact":0,
            "hardness":0,
            "resistivity":0,
            "cleanness":0,
            "decarburisation":0,
            "sulphur":0,
            "hydrogen":0,
            "prodan":0,
        }
        response = self.client.post(self.host_url + "/test/", json=data, headers=headers)
        assert response.status_code == 200
        test_id_5 = response.json()['id']

        #创建test tensile
        data = {
            "test_sample_id":test_sample_id_1,
            "mill_id": 1,
            "code":'0',
            "value_mpa":500,
            "test_id":test_id_1,
            "sample_shape":'1',
            "tested_thickness":10,
            "tested_width":10,
            "tested_diameter":10,
            "yield_tt0_5": 400,
            "yield_high":500,
            "yield_rp0_2":300,
            "yield_low":300,
            "elongation_code":'Y',
            "elongation_a565":50,
            "elongation_a200":50,
            "elongation_a50":50,
            "elongation_8":50,
            "elongation_2":50,
            "elongation_a80":50,
        }
        response = self.client.post(self.host_url + "/test_tensile/", json=data, headers=headers)
        assert response.status_code == 200
        test_tensile = response.json()['id']

        #创建test impact
        data = {
            "test_sample_id": test_sample_id_2,
            "mill_id": 1,
            "retest_seq":0,
            "test_id":test_id_2,
            "temp_c":20,
            "energy_1_j":50,
            "energy_2_j":50, 
            "energy_3_j":50,
            "energy_average_j":50
        }
        response = self.client.post(self.host_url + "/test_impact/", json=data, headers=headers)
        assert response.status_code == 200
        test_impact_1 = response.json()['id']

        data = {
            "test_sample_id": test_sample_id_3,
            "mill_id": 1,
            "retest_seq":0,
            "test_id":test_id_3,
            "temp_c":0,
            "energy_1_j":50,
            "energy_2_j":50, 
            "energy_3_j":50,
            "energy_average_j":50
        }
        response = self.client.post(self.host_url + "/test_impact/", json=data, headers=headers)
        assert response.status_code == 200
        test_impact_2 = response.json()['id']

        data = {
            "test_sample_id": test_sample_id_4,
            "mill_id": 1,
            "retest_seq":0,
            "test_id":test_id_4,
            "temp_c":-20,
            "energy_1_j":50,
            "energy_2_j":50, 
            "energy_3_j":50,
            "energy_average_j":50
        }
        response = self.client.post(self.host_url + "/test_impact/", json=data, headers=headers)
        assert response.status_code == 200
        test_impact_3 = response.json()['id']

        data = {
            "test_sample_id": test_sample_id_5,
            "mill_id": 1,
            "retest_seq":0,
            "test_id":test_id_5,
            "temp_c":-40,
            "energy_1_j":50,
            "energy_2_j":50, 
            "energy_3_j":50,
            "energy_average_j":50
        }
        response = self.client.post(self.host_url + "/test_impact/", json=data, headers=headers)
        assert response.status_code == 200
        test_impact_4 = response.json()['id']


        # #SCT Covering
        # response = self.client.post(self.host_url + f"/cover_end_use/init_test/{runout_id}", json=data, headers=headers)
        # assert response.status_code == 200
        
        # finished_product_1 = self.db_session.query(FinishedProduct).filter(FinishedProduct.id == finished_product_id_1).first()
        # assert finished_product_1.t_result == 9
        # assert finished_product_1.c_result == 9

        data = {}
        response = self.client.post(self.host_url + "/menu/data/init_menu_button_settings", json=data, headers=headers)
        assert response.status_code == 200

        log.info("over all success")


if __name__ == "__main__":
    a = OverAllAPI()
    a.delete_database()
    a.test_semi_all()


