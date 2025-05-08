import json
import locale
import requests
# import pymqi 如果需要请取消注释  报错：ModuleNotFoundError: No module named 'pymqi'
import time
from dispatch.config import ENABLE_MESSAGE_FORWARD, FORWARD_URLS, MQ_LIMIS_ENDPOINTS_READ, MQ_LIMIS_ENDPOINTS_WRITE
from dispatch.database_util.service import get_schema_session
from dispatch.message_admin.message.ibmmq.mq_service import save_message_to_mq
from dispatch.message_admin.message_log import service as message_log_service
from dispatch.message_admin.message_log.models import MessageLogCreate
from dispatch.mill import service as mill_service
from dispatch.mill.models import MillCreate
from dispatch import config
from dispatch.log import getLogger
log = getLogger(__name__)

EnablePymqi = True
try:
    import pymqi
    log.info('pymqi is installed and imported successfully!')
except Exception as e:
    pymqi = None
    EnablePymqi = False
    log.warning('pymqi is not installed and imported failed!')

def connect(type="read"):
    if type == "read":
        MQ_LIMIS_ENDPOINTS = MQ_LIMIS_ENDPOINTS_READ
    else:
        MQ_LIMIS_ENDPOINTS = MQ_LIMIS_ENDPOINTS_WRITE
    try:
        locale.setlocale(locale.LC_ALL, "en_GB.ISO-8859-1")
    except Exception as e:
        pass
    
    log.info('Establishing Connection with MQ Server')
    queue_manager = MQ_LIMIS_ENDPOINTS['QUEUE_MANAGER']
    channel = MQ_LIMIS_ENDPOINTS['CHANNEL']
    host = MQ_LIMIS_ENDPOINTS['HOST']
    port = MQ_LIMIS_ENDPOINTS['PORT']
    user = MQ_LIMIS_ENDPOINTS['APP_USER']
    password = MQ_LIMIS_ENDPOINTS['APP_PASSWORD']
    conn_info = '%s(%s)' % (host, port)

    # Read from MQ
    qmgr = pymqi.connect(queue_manager, channel, conn_info, user, password)
    return qmgr

def getQueue(qmgr, queue_name):
    log.info('Connecting to Queue')
    try:
        queue = pymqi.Queue(qmgr, queue_name)
        if not queue:
            raise Exception('Can not get pymqi')
        log.info('Connected to queue ' + str(queue_name))
        return queue
    except pymqi.MQMIError as e:
        log.error("Error getting queue")
        log.error(e)
        return None

def forward_lims_message(message_str):
    if not ENABLE_MESSAGE_FORWARD:
        return
    log.info(f'FORWARD_URLS lims are: {FORWARD_URLS}, message_str: {message_str}')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEwMzc3NjQ5NTU5Ljc5ODE0MSwiZW1haWwiOiJtZXNfcm9vdEBicml0aXNoc3RlZWwuY28udWsiLCJvcmdfY29kZSI6Im1lc19yb290Iiwib3JnX2lkIjoxMDEsInJvbGUiOlsic3lzIl0sImRlZmF1bHRfdGVhbV9pZCI6MSwiY3VycmVudF9taWxsX2lkIjoxfQ.t8VUoQpHs-BkJVCq_7TOHlMZnFc8U01aY900zZuhfSE"
    }
    
    for url in FORWARD_URLS:
        if url.endswith("/"):
            url = url[:-1]
        url = url + '/api/v1/message/test_receive_from_lims'
        
        try:
            message_body = {
                'messages': [message_str]
            }
            
            response = requests.post(url, json=message_body, headers=headers, timeout=5)
            log.info(f"Response status: {response.status_code}, Response body: {response.text}")
            
        except Exception as e:
            log.error(f'Error forwarding message to lims: {e}')


try:
    from dispatch.contrib.message_admin.message.lims import transform_decrypt_message, transform_encrypt_message

    def read_mq():
        queue_name = MQ_LIMIS_ENDPOINTS_READ['QUEUE_NAME']

        # Initialize MQ connection and queue
        def init_connection():
            try:
                qmgr = connect()
                queue = getQueue(qmgr, queue_name)
                log.info("MQ connection established successfully.")
                return qmgr, queue
            except Exception as e:
                log.error(f"Failed to initialize MQ connection: {e}")
                time.sleep(30)
                return None, None

        qmgr, queue = init_connection()

        desc = pymqi.MD()
        desc.CodedCharSetId = 819  # Set message encoding charset

        gmo = pymqi.GMO()
        gmo.Options = pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
        gmo.WaitInterval = 5000  # Wait up to 5 seconds for a message

        org_db_session = get_schema_session(org_code=MQ_LIMIS_ENDPOINTS_READ['DB_ORG_CODE'])

        while True:
            try:
                # Re-establish connection if not available
                if not qmgr or not queue:
                    qmgr, queue = init_connection()
                    if not qmgr:
                        continue

                # Read message from MQ
                message = queue.get(None, desc, gmo)
                de_message = message.decode('utf-8')
                log.info(f"Received message: {de_message}")

                # Forward and decrypt the message
                forward_lims_message(de_message)
                message_code, decrypted_message = transform_decrypt_message(de_message)

                if not decrypted_message:
                    log.error(f'decrypted_message is None, raw message: {de_message}')
                    continue

                # Determine mill code by sample type
                sample_type = decrypted_message.get("Sample Type", "B")
                mill_code = "SKG" if sample_type == "S" else "TBM"
                mill = mill_service.get_by_code(db_session=org_db_session, code=mill_code)
                if not mill:
                    mill_in = MillCreate(code=mill_code, type=mill_code, desc=mill_code)
                    mill = mill_service.create(db_session=org_db_session, mill_in=mill_in)

                # Log message into database
                message_log_in = MessageLogCreate(
                    mill=mill,
                    message_id=int(message_code),
                    type="lims",
                    msg=de_message,
                    message_json=json.dumps(decrypted_message, ensure_ascii=False),
                    interact="LIMS to MES",
                    updated_by="system",
                    created_by="system",
                    message_status="Receive"
                )
                message_log_service.create(db_session=org_db_session, message_log_in=message_log_in)

                # Save message to another MQ queue or DB
                save_message_to_mq(org_db_session, message_code, decrypted_message)

            except pymqi.MQMIError as e:
                time.sleep(5)
                if e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    # No message in queue – ignore
                    pass
                elif e.reason == pymqi.CMQC.MQRC_HOST_NOT_AVAILABLE:
                    log.error(f"MQ Host not available: {MQ_LIMIS_ENDPOINTS_READ['HOST']}")
                elif e.reason == pymqi.CMQC.MQRC_CONNECTION_BROKEN:
                    log.error("MQ connection broken. Attempting to reconnect...")
                    try:
                        qmgr.disconnect()
                    except Exception as e2:
                        log.warning(f"Failed to disconnect old connection: {e2}")
                    qmgr, queue = init_connection()
                elif e.reason == pymqi.CMQC.MQRC_HCONN_ERROR:
                    log.error("MQRC_HCONN_ERROR: Invalid connection handle. Reconnecting...")
                    try:
                        qmgr.disconnect()
                    except Exception as e2:
                        log.warning(f"Failed to disconnect old connection: {e2}")
                    qmgr, queue = init_connection()
                else:
                    log.error(f"Unhandled MQ error: {e}")

            except Exception as e:
                time.sleep(5)
                log.error(f"Unexpected error occurred: {e}")

            finally:
                # Reset message descriptor fields for next read
                desc.MsgId = pymqi.CMQC.MQMI_NONE
                desc.CorrelId = pymqi.CMQC.MQCI_NONE
                desc.GroupId = pymqi.CMQC.MQGI_NONE



    def write_mq(message_dict):
        """
        Writes a transformed and encoded message to an MQ queue.
        Args:
            message_dict (dict): The dictionary containing the message details.
        """
                # Transform and encrypt the message
        message = transform_encrypt_message(message_dict)
        log.info(f'Current MQ status: {config.MQ_LIMIS_ENDPOINTS_WRITE['ON_OFF']}, and MQ configuration: {config.MQ_LIMIS_ENDPOINTS_WRITE}')
        if not message:
            log.error(f"Transformed message is empty or invalid. message_dict: {message_dict}, message: {message}")
            return
        if config.MQ_LIMIS_ENDPOINTS_WRITE['ON_OFF']:
            qmgr = None
            queue = None
            try:
                org_db_session = get_schema_session(org_code=MQ_LIMIS_ENDPOINTS_WRITE['DB_ORG_CODE'])

                mill_code = "TBM"
                mill = mill_service.get_by_code(db_session=org_db_session, code=mill_code)
                if not mill:
                    mill_in = MillCreate(
                        code=mill_code,
                        type=mill_code,
                        desc=mill_code,

                    )
                    mill = mill_service.create(db_session=org_db_session, mill_in=mill_in)

                message_log_in = MessageLogCreate(
                        message_id=int(message_dict["Message Type"]),
                        type="lims",
                        mill=mill,
                        msg=str(message),
                        interact="MES to LIMS",
                        updated_by="MES",
                        created_by="MES",
                        message_json=str(message_dict),
                        message_status="Send"
                        )
                # Encode the message in ISO 8859-1
                encoded_message = message.encode("iso-8859-1")
                log.info(f"Encoded message: {encoded_message}")

                # Retrieve queue name from configuration
                queue_name = MQ_LIMIS_ENDPOINTS_WRITE.get('QUEUE_NAME')
                if not queue_name:
                    raise ValueError("Queue name is missing in MQ_LIMIS_ENDPOINTS_WRITE configuration.")

                # Connect to MQ
                qmgr = connect("write")
                if not qmgr:
                    # raise ConnectionError("Failed to connect to MQ.")
                    log.error(f'Failed to connect to MQ. Sending message {message} failed! Because qmgr is null')
                    return

                # Create Message Descriptor with CCSID 819
                desc = pymqi.MD()
                desc.CodedCharSetId = 819  # Set to ISO 8859-1
                desc.Format = pymqi.CMQC.MQFMT_STRING  # Set format to MQFMT_STRING

                queue = pymqi.Queue(qmgr, queue_name)
                queue.put(encoded_message, desc)
                message_log_in.message_status = "Success"
                log.info(f"Message sent successfully to queue '{queue_name}': {encoded_message.decode('iso-8859-1')} and closed the connection to the queue.")

                message_log_service.create(db_session=org_db_session, message_log_in=message_log_in)

            except pymqi.MQMIError as mq_error:
                log.error(f"MQ error occurred: {mq_error}")
                raise

            except Exception as e:
                log.error(f"An error occurred while writing to MQ: {e}")
                raise

            finally:
                # Ensure the queue manager is disconnected
                if queue:
                    try:
                        queue.close()
                        log.info("Queue closed successfully.")
                    except Exception as e:
                        log.info(f"Failed to close queue: {e}")
                if qmgr:
                    try:
                        qmgr.disconnect()
                        log.info("Disconnected from MQ queue manager.")
                    except Exception as e:
                        log.error(f"Failed to disconnect MQ queue manager: {e}")
        else:
             log.error(f'Failed to connect to MQ. Sending message {message} failed! Because MQ is off')
except ImportError as e:
    def read_mq():
        raise NotImplementedError("read_mq is not available because required modules are missing.")
    def write_mq(message_dict):
        raise NotImplementedError("write_mq is not available because required modules are missing.")

if __name__ == "__main__":
    message = '140|03-OCT-2024 12:56:00|0156|836700|F|UCx0356x0368x0177|6V76265 |76265|023.8|L|BSEN|   |0|1|22.67|20.37|     |0492|0372|0410|0377|0371|Z|31|  |  |  |  |  |'
    org_db_session = get_schema_session(org_code=MQ_LIMIS_ENDPOINTS_READ['DB_ORG_CODE'])  
    
    code, decrypted_message = transform_decrypt_message(message)
    if not decrypted_message:
        log.error(f'decrypted_message is None, de_message is {decrypted_message}')
    else:
        log.info(f'decrypted_message: {decrypted_message}')
        write_mq(decrypted_message)
