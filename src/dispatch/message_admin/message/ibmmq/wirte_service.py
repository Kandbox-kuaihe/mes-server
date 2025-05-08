from datetime import datetime
import json
import logging


from dispatch.config import MQ_LIMIS_ENDPOINTS_WRITE
from dispatch.message_admin.message.ibmmq.mq_tools import write_mq
from dispatch.message_admin.message_log import service as message_log_service
from dispatch.message_admin.message_log.models import MessageLogCreate
from dispatch.mill import service as mill_service
from dispatch.tests_admin.test_result_impact import (
    service as test_result_impact_service,
)
from dispatch.tests_admin.test_result_tensile import (
    service as test_result_tensile_service,
)
from dispatch.tests_admin.test_result_tensile_thickness import (
    service as test_result_tensile_thickness_service,
)
from dispatch.tests_admin.test_sample import service as test_sample_service
from dispatch.spec_admin.sptensil import service as sptensile_service
from dispatch.spec_admin.spria import service as spria_service
from dispatch.spec_admin.spimpact import service as spimpact_service
from dispatch.tests_admin.test_sample.models import TestSampleCreate


 
from dispatch.log import getLogger
log = getLogger(__name__)


class WriteMessageToMq():

    """
    send message to mq lims 
    """

    def __init__(self,db_session,test_sample_id,spec_id):
        self.test_sample_id = test_sample_id
        self.spec_id = spec_id
        self.db_session = db_session
        self.test_sample = None
        self.sptensile = None
        self.spimpact = None
        self.spria = None

    def get_test_sample(self):
        if self.test_sample: return
        self.test_sample = test_sample_service.get(db_session=self.db_session,testSample_id=self.test_sample_id)
    
    def get_sptensile(self):
        if not self.spec_id: return None
        self.sptensile_list = sptensile_service.get_by_spec_id(db_session=self.db_session,spec_id=self.spec_id)
        self.sptensile = self.sptensile_list[0] if self.sptensile_list else None
    
    def get_spimpact(self):
        if not self.spec_id: return None
        self.spimpact_list = spimpact_service.get_by_spec_id(db_session=self.db_session,spec_id=self.spec_id)
        self.spimpact = self.spimpact_list[0] if self.spimpact_list else None
    
    def get_spria(self):
        if not self.spec_id: return None
        self.spria_list = spria_service.get_by_spec_id(db_session=self.db_session,spec_id=self.spec_id)
        self.spria = self.spria_list[0] if self.spria_list else None
    
    def get_write_message(self,message_type,error_reason = None,reply_to = 123):
        '''
        '''
        dt = datetime.now()
        self.message_time = dt.strftime('%d-%b-%Y %H:%M:%S')
        
        if self.test_sample_id is None:
            return None
        self.get_test_sample() 
        if self.test_sample is None:
            return None
        if message_type == 120:
            return self.message120_to_mq() 
        elif message_type == 125:
            return self.message125_to_mq(error_reason)    
        elif message_type == 130:
            self.get_sptensile()
            return self.message130_to_mq(reply_to)
        elif message_type == 131:
            self.get_spimpact()
            return self.message131_to_mq(reply_to)
        elif message_type == 133:
            self.get_spria()
            return self.message133_to_mq(reply_to)
        else:
            return None

    def write_message_to_lims(self,message_type,error_reason = None,reply_to = 123):
        status = "ok"
        msg = ""
        try:
            if  MQ_LIMIS_ENDPOINTS_WRITE['ON_OFF']: 
                message_data = self.get_write_message(message_type,error_reason,reply_to)
                print(f'Get message data:  {message_data}')
                def process_single_message(message_dict):
                    if message_dict:
                        write_mq(message_dict)  # 将消息写入 MQ
                        msg = json.dumps(message_dict)
                    else:
                        test_sample_in = TestSampleCreate(
                            id=self.test_sample_id if self.test_sample_id else None,
                            spec_id=self.spec_id,
                        )
                        test_sample = test_sample_service.create(db_session=self.db_session, testSample_in=test_sample_in)
                        msg = f"Write MQ, created test_sample, id: {self.test_sample_id or test_sample.id}"
                        log.info(msg)
                    # 创建消息日志 重复了注释
                    # message_log_in = MessageLogCreate(
                    #     message_id=message_type,
                    #     type="lims",
                    #     msg="",
                    #     message_json=msg,
                    #     interact="MES to LIMS",
                    #     updated_by="system",
                    #     created_by="system",
                    # )
                    # message_log_service.create(db_session=self.db_session, message_log_in=message_log_in)

                # 统一处理 message_data
                if isinstance(message_data, list):
                    for message_dict in message_data:
                        process_single_message(message_dict)
                else:
                    process_single_message(message_data)
            else:
                status = "fail"
                msg = "MQ is off"

        except Exception as e:
            status = "fail"
            msg = str(e)

        return status, msg
        
    def message120_to_mq(self):
        '''
        '''
        result = {
            "Message Type": "120",
            "Message Time": self.message_time,
            "Message Length": "0096",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Flange Sample 1": "F" if self.test_sample.flange_thickness1 else None,
            "Flange Thickness 1": self.test_sample.flange_thickness1,
            "Flange Sample 2": "F" if self.test_sample.flange_thickness2 else None,
            "Flange Thickness 2": self.test_sample.flange_thickness2,
            "Web Sample": "W" if self.sptensil and self.sptensil.location == "W" else None,
            "Web Thickness": self.test_sample.web_thickness if self.sptensil and self.sptensil.location == "W" else None,
        }
        return result

    def message125_to_mq(self,error_reason = ""):
        '''
        {
        "Message Type": "125",
        "Message Time": "10-OCT-2024 00:09:44",
        "Message Length": "0118",
        "Piece ID": "829968",
        "Piece Sub ID": "F",
        "Product String": "UBx0406x0140x0039",
        "Cast ID": "6V75314",
        "Concast No": "75314",
        "Sample Thickness": "008.6",
        "Short Name": "",             
        "Inspector": "",
        "Error Reason": "No tests found for bar 829968"   
    }
    125|10-OCT-2024 00:09:44|0118|829968|F|UBx0406x0140x0039|6V75314 |75314|008.6|    |   |No tests found for bar 829968 |
        ''' 
        result = {
            "Message Type": "125",
            "Message Time": self.message_time,
            "Message Length": "0118",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Sample Thickness": self.test_sample.sample_thickness,
            "Short Name": self.test_sample.spec_name,
            "Inspector": self.test_sample.inspector,
            "Error Reason": error_reason
        }
        return result
    def message126_to_mq(self):
        '''
        {
    "Message Type": "126",
    "Message Time": "03-OCT-2024 09:20:40",
    "Message Length": "0121",
    "Piece ID": "826496",
    "Piece Sub ID": "Empty",
    "Product String": "UCx0356x0368x0177",
    "Cast ID": "6V76265",
    "Concast No": "76265",
    "Flange Sample 1": "F",
    "Falnge Thickness 1": "023.8",
    "Flange Sample 2": "Empty",
    "Falnge Thickness 2": "000.0",
    "Web Sample": "Empty",
    "Web Thickness": "000.0",
    "Request Number": "TD17",                        ??
    "Sample Size": "500",                        ??
    "Spec": "HNK2",                         
    "Inspector": "Empty",                        
    "Sample Location": "BS06"                        ??
}
126|03-OCT-2024 09:20:40|0121|826496|Empty|UCx0356x0368x0177|6V76265|76265|F|023.8|Empty|000.0|Empty|000.0|TD17|500|HNK2|Empty|BS06
        '''
        result = {
            "Message Type": "126",
            "Message Time": self.message_time,
            "Message Length": "0121",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Flange Sample 1": self.test_sample.flange_sample1,
            "Flange Thickness 1": self.test_sample.flange_thickness1,
            "Flange Sample 2": self.test_sample.flange_sample2,
            "Flange Thickness 2": self.test_sample.flange_thickness2,
            "Web Sample": self.test_sample.web_sample,
            "Web Thickness": self.test_sample.web_thickness,
            "Request Number": "TD17",
            "Sample Size": "500",
            "Spec": self.test_sample.spec_name,
            "Inspector": self.test_sample.inspector,
            "Sample Location": "BS06"
        }
        return result
    
    def message128_to_mq(self):
        '''
        '''
        result = {
            "Message Type": "128",
            "Message Time": self.message_time,
            "Message Length": "0121",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Flange Sample 1": self.test_sample.flange_sample1,
            "Flange Thickness 1": self.test_sample.flange_thickness1,
            "Flange Sample 2": self.test_sample.flange_sample2,
            "Flange Thickness 2": self.test_sample.flange_thickness2,
            "Web Sample": self.test_sample.web_sample,
            "Web Thickness": self.test_sample.web_thickness,
            "Request Number": "TD17",
            "Sample Size": "500",
            "Spec": self.test_sample.spec_name,
            "Inspector": self.test_sample.inspector,
            "Sample Location": "BS06"
        }
        return result



    def message130_to_mq(self,reply_to):
        '''
        {
    "Message Type": "130",
    "Message Time": "03-OCT-2024 01:37:35",
    "Message Length": "0353",
    "Piece ID": "829395",
    "Piece Sub ID": "F",
    "Product String": "UBx0610x0229x0125",
    "Cast ID": "6V76844",
    "Concast No": "7",
    "Sample Thickness": "Empty",
    "Reply To": "Empty",                ????
    "Message Type 1": "Empty",           ????
    "Message Seg": "84",               ????
    "Retest": "|",
    "Orientation": "1",
    "Standard": ".6|T",
    "Inspector": "S|0",
    "Inspector Longname": "| |L|BSEN|   |",
    "Specification Details": "|S3",
    "Specification Code": "7 |J",
    "Specification Name": "35|S",

    "Product Anyalysis Flag": "Empty", 
    "Thickness Min": "Empty",
    "Thickness Max": "Empty",
    "Elong Code 1 Min": "|",
    "Elong Code 2 Min": "18",
    "Elong Code 3 Min": "1|",
    "Elong Code 4 Min": "22",
    "Elong Code 5 Min": "1|",
    "Elong Code 6 Min": "2|",
    "Tensile Min": "|  |  |",          ??????
    "Tensile Max": "|  |000",    ??????
    "Tensile Units": "7",   ??????
    "Yield Min": ".0|00063",   ??????
    "Yield Max": ".0|M|000",   ??????
    "Yield Units": "4",   ??????
    "Y T Ratio Min": ".0|",   ??????
    "Y T Ratio Max": "Empty"   ??????
}
130|03-OCT-2024 01:37:35|0353|829395|F|UBx0610x0229x0125|6V76844|7|Empty|Empty|Empty|84|||1|.6|T|S|0|| |L|BSEN|   |||S3|7 |J|35|S|Empty|Empty|Empty|||18|1||22|1||2|||  |  |||  |000|7|.0|00063|.0|M|000|4|.0||Empty|
        '''
        if self.sptensile is None:
            return None
        result = {
            "Message Type": "130",
            "Message Time": self.message_time,
            "Message Length": "0365",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Sample Thickness": self.test_sample.sample_thickness,
            "Reply To": "T" if  reply_to ==123 else "O",                    
            "Message Type 1": "S",
            "Message Seg": "01",
            "Retest": self.test_sample.retest,
            "Orientation": self.test_sample.orientation,
            "Standard": self.test_sample.standard,
            "Inspector": self.test_sample.inspector,
            "Inspector Longname":  self.test_sample.inspector_longname,
            "Specification Details":self.test_sample.spec_details,
            "Specification Code": self.test_sample.spec.spec_code,
            "Specification Name": self.test_sample.spec_name,

            "Product Anyalysis Flag": self.sptensile.product_analysis_flag,
            "Thickness Min": self.sptensile.thick_from,
            "Thickness Max": self.sptensile.thick_to,
            "Elong Code 1 Min": self.sptensile.elong_code_1_min,
            "Elong Code 2 Min": self.sptensile.elong_code_2_min,
            "Elong Code 3 Min": self.sptensile.elong_code_3_min,
            "Elong Code 4 Min": self.sptensile.elong_code_4_min,
            "Elong Code 5 Min": self.sptensile.elong_code_5_min,
            "Elong Code 6 Min": self.sptensile.elong_code_6_min,
            "Tensile Min": self.sptensile.tensile_min,
            "Tensile Max": self.sptensile.tensile_max,
            "Tensile Units": self.sptensile.tensile_units,
            "Yield Min": self.sptensile.yield_min,
            "Yield Max": self.sptensile.yield_max,
            "Yield Units": self.sptensile.yield_units,
            "Y T Ratio Min": self.sptensile.y_t_ratio_min,
            "Y T Ratio Max": self.sptensile.y_t_ratio_max
        }
        return result
    
    def message131_to_mq(self,reply_to):
        '''
        TODO Message Type 131
        '''

        if self.spimpact is None:
            return None

        result = {
            "Message Type": "131",
            "Message Time": self.message_time,
            "Message Length": "0314",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Sample Thickness": self.test_sample.sample_thickness,
            "Reply To": "T" if  reply_to ==123 else "O",                    
            "Message Type 1": "S",
            "Message Seg": "01",
            "Retest": self.test_sample.retest,
            "Orientation": self.test_sample.orientation,
            "Standard": self.test_sample.standard,
            "Inspector": self.test_sample.inspector,
            "Inspector Longname":  self.test_sample.inspector_longname,
            "Specification Details":self.test_sample.spec_details,
            "Specification Code": self.test_sample.spec.spec_code,
            "Specification Name": self.test_sample.spec_name
        }
        result_list = []
        for i in range(1,6):
            column = "temp_value_" + str(i)
            if hasattr(self.spimpact, column) and getattr(self.spimpact, column):
                _result = {
                    "Charpy Temp": getattr(self.spimpact, "temp_value_"+str(i)),
                    "Charpy Temp Units": getattr(self.spimpact, "temp_units"),
                    "Charpy Ave": getattr(self.spimpact, "ave_value_"+str(i)),
                    "Charpy Min": getattr(self.spimpact, "min_value_"+str(i)),
                    "Charpy I Units": getattr(self.spimpact, "impact_units"),
                    "Shear Required": "Y",
                    "Shear Min": getattr(self.spimpact, "min_shear_"+str(i)),
                    "Shear Ave Min": getattr(self.spimpact, "ave_shear_"+str(i)),
                }
                _result.update(result)
                _result["Message Seg"] = f"0{i}"
                if i ==0:
                    _result["Message Type 1"] = "S"
                elif i == 6:
                    _result["Message Type 1"] = "E"
                else :
                    _result["Message Type 1"] = "M"
                result_list.append(_result)
                
        if result_list and len(result_list) > 1:
             result_list[-1]["Message Type 1"] = "E"

        return result_list 
        
    def message133_to_mq(self,reply_to):
        '''
        TODO Message Type 133
        '''
        
        if self.spria is None:
            return None
        result = {
            "Message Type": "130",
            "Message Time": self.message_time,
            "Message Length": "0287",
            "Piece ID": self.test_sample.test_sample_code,
            "Piece Sub ID": self.test_sample.test_sample_part,
            "Product String": self.test_sample.product_name,
            "Cast ID": self.test_sample.cast.cast_code,
            "Concast No": self.test_sample.concast_code,
            "Sample Thickness": self.test_sample.sample_thickness,
            "Reply To": "T" if  reply_to ==123 else "O",                    
            "Message Type 1": "S",
            "Message Seg": "01",
            "Retest": self.test_sample.retest,
            "Orientation": self.test_sample.orientation,
            "Standard": self.test_sample.standard,
            "Inspector": self.test_sample.inspector,
            "Inspector Longname":  self.test_sample.inspector_longname,
            "Specification Details":self.test_sample.spec_details,
            "Specification Code": self.test_sample.spec.spec_code,
            "Specification Name": self.test_sample.spec_name,

            "Reduction In Area Min": self.spria.ria_min_value,
            "Reduction In Area Ave": self.spria.ria_ave_value, 
        }
        return result 