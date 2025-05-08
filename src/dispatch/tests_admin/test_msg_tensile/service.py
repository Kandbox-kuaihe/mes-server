from dispatch.tests_admin.test_list import service as test_list_service



def trigger_m362(
    *,
    db_session,
    test_id: int,
    background_tasks,
    current_mill_code
):

    #test_msg_tensile = db_session.get(TestMsgTensile, test_id)
    test1 = test_list_service.get(db_session=db_session, id=test_id)
    #m362_msg_info = {
    #    "retest_seq": 1,
    #    "check_digit": 1,
    #    "test_number": 7,
    #    "thickness": 6,
    #    "width": 6,
    #    "diameter": 6,
    #   "inner_diameter": 6,
    #    "area": 6,
    #    "pl_length": 6,
    #    "initial_gauge_length": 6,
    #    "calculated_area": 6,
    #    "uts_kn": 7,
    #    "yield_a": 7,
    #    "lower_yield": 7,
    #    "rp1": 7,
    #    "rp2": 7,
    #    "rt5": 7,
    #    "final_gauge_length": 6,
    #    "z": 6,
    #    "elongation": 6,
    #    "a565": 7,
    #    "uts_load": 7,
    #    "yield_load": 7,
    #    "lower_yield_load": 7,
    #    "rp1_load": 7,
    #    "rp2_load": 7,
    #    "rt5_load": 7,
    #    "prompt1": 10,
    #    "prompt2": 10,
    #    "prompt3": 10,
    #    "prompt4": 15,
    #    "prompt5": 15,
    #    "reply1": 10,
    #    "reply2": 10,
    #    "reply3": 10,
    #    "reply4": 20,
    #    "reply5": 20,
    #    "at": 6,
    #    "ae": 6,
    #    "ag": 6,
    #    "agt": 6,
    #    "weight": 7,
    #    "length": 6,
    #    "density": 9,
    #    "initial_agt": 6,
    #    "final_agt": 6,
    #    "final_diameter": 6,
    #    "e_rate": 6,
    #    "p_rate1": 6,
    #    "p_rate2": 6,
    #    "p_rate3": 6,
    #    "status": 4,
    #    "prompt6": 15,
    #    "reply6": 20,
    #    "config_file": 8,
    #    "ra2": 6,
    #    "ra3": 6,
    #    "ra4": 6,
    #    "ra5": 6,
    #    "ra6": 6,
    #    "uts2": 7,
    #    "uts3": 7,
    #    "uts4": 7,
    #    "uts5": 7,
    #    "uts6": 7,
    #    "ys2": 7,
    #    "ys3": 7,
    #    "ys4": 7,
    #    "ys5": 7,
    #    "ys6": 7
    #}
    try:
        from dispatch.contrib.message_admin.message_server import server as MessageServer
        srsmm362 = MessageServer.MessageStrategySRSMM362()
        srsmm362.send_pc_m362(db_session=db_session, test_code=test1.test_code, background_tasks=background_tasks, current_mill_code=current_mill_code)
        #msg_in = {}
        #for key in m362_msg_info.keys():
        #    value = getattr(test1, key)
        #    if isinstance(value, Decimal):
        #        msg_in[key] = float(value)
        #    else:
        #        msg_in[key] = value
        #handle_m362(db_session=db_session, msg_in=msg_in, background_tasks=background_tasks)
        return True
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))