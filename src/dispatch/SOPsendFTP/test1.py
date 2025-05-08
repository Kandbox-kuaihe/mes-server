from dispatch.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from dispatch.order_admin.order.models import Order
from dispatch.order_admin.order_item.models import OrderItem
from dispatch.semi_admin.semi.models import Semi
from dispatch.semi_admin.semi_load.models import SemiLoad
from dispatch.cast.models import Cast
from datetime import datetime
import psycopg2
import string
# Mapping dictionary

# Function to get the mapped output
def get_transport_code(transport_type):
    transport_mapping = {
    "Truck (TMS)": "B",
    "Truck (Non TMS)": "B",
    "Rail": "G",
    "Conv. Vessel": "R",
    "Airplane": "R",
    "Container": "R",
    "Unit load (Truck)": "U",
    "Customer Collect": "O"
}

    return transport_mapping.get(transport_type, " ")  # Default to ' ' if not found

def get_incoterm_code(incoterm):
    incoterm_mapping = {
        "CFR": "145",
        "CIF": "149", 
        "CIP": "143",
        "CPT": "153",
        "DAP": "154",
        "DAT": "157",
        "DDP": "134", 
        "DDU": "002", 
        "EXW": "050",
        "FAS": "070",
        "FCA": "060",
        "FOB": "082", 
        "PHM": "154",
        "DPU": "154"
    }

    return incoterm_mapping.get(incoterm, "   ")  # Default to ' ' if not found

def rollingweekyear(rollingcode):
    
    if rollingcode.startswith("P"):
        letter = rollingcode[3]
        letters = string.ascii_uppercase  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letter_year_mapping = {
            #我不懂， 2048再说吧
            letter: 2023 + (ord(letter) - ord('A'))
            for letter in letters
        }
        year = letter_year_mapping[letter]  # 2025
        # nextyear
        next_year = (year + 1) % 100  # avoid overflow 99 + 1 -> 00
        next_year = f"{next_year:02d}"
        return rollingcode[1:3]+next_year
    else:
        return '9999'

def get_transport_code(transport_type):
    transport_mapping = {
    "Truck (TMS)": "B",
    "Truck (Non TMS)": "B",
    "Rail": "G",
    "Conv. Vessel": "R",
    "Airplane": "R",
    "Container": "R",
    "Unit load (Truck)": "U",
    "Customer Collect": "O"
}

    return transport_mapping.get(transport_type, " ")  # Default to ' ' if not found

def get_country_code(iso_code_sap):

    country_mapping = {
        "FR": "001",
        "BE": "002",
        "NL": "003",
        "DE": "004",
        "IT": "005",
        "GB": "006",
        "IE": "007",
        "DK": "008",
        "GR": "009",
        "PT": "010",
        "ES": "011",
        "LU": "019",
        "IC": "021",
        "CE": "022",
        "IS": "024",
        "NO": "028",
        "SE": "030",
        "FI": "032",
        "LI": "037",
        "AT": "038",
        "CH": "039",
        "FO": "041",
        "AD": "043",
        "GI": "044",
        "VA": "045",
        "MT": "046",
        "SM": "047",
        "TR": "052",
        "EE": "053",
        "LV": "054",
        "LT": "055",
        "PL": "060",
        "CZ": "061",
        "SK": "063",
        "HU": "064",
        "RO": "066",
        "BG": "068",
        "AL": "070",
        "UA": "072",
        "BY": "073",
        "MD": "074",
        "RU": "075",
        "GE": "076",
        "AM": "077",
        "AZ": "078",
        "KZ": "079",
        "TM": "080",
        "UZ": "081",
        "TJ": "082",
        "KG": "083",
        "SI": "091",
        "HR": "092",
        "BA": "093",
        "CS": "094",
        "MK": "096",
        "ME": "097",
        "RS": "098",
        "MA": "204",
        "DZ": "208",
        "TN": "212",
        "LY": "216",
        "EG": "220",
        "SD": "224",
        "MR": "228",
        "ML": "232",
        "BF": "236",
        "NE": "240",
        "TD": "244",
        "CV": "247",
        "SN": "248",
        "GM": "252",
        "GW": "257",
        "GN": "260",
        "SL": "264",
        "LR": "268",
        "CI": "272",
        "GH": "276",
        "TG": "280",
        "BJ": "284",
        "NG": "288",
        "CM": "302",
        "CF": "306",
        "GQ": "310",
        "ST": "311",
        "GA": "314",
        "CG": "318",
        "ZR": "322",
        "RW": "324",
        "BI": "328",
        "SH": "329",
        "AO": "330",
        "ET": "334",
        "ER": "336",
        "DJ": "338",
        "SO": "342",
        "KE": "346",
        "UG": "350",
        "TZ": "352",
        "SC": "355",
        "IO": "357",
        "MZ": "366",
        "MG": "370",
        "RE": "372",
        "MU": "373",
        "KM": "375",
        "YT": "377",
        "ZM": "378",
        "ZW": "382",
        "MW": "386",
        "ZA": "388",
        "NA": "389",
        "BW": "391",
        "SZ": "393",
        "LS": "395",
        "US": "400",
        "CA": "404",
        "GL": "406",
        "PM": "408",
        "MX": "412",
        "BM": "413",
        "GT": "416",
        "BZ": "421",
        "HN": "424",
        "SV": "428",
        "NI": "432",
        "CR": "436",
        "PA": "442",
        "AI": "446",
        "CU": "448",
        "KN": "449",
        "HT": "452",
        "BS": "453",
        "TC": "454",
        "DO": "456",
        "VI": "457",
        "GP": "458",
        "AG": "459",
        "DM": "460",
        "MQ": "462",
        "KY": "463",
        "JM": "464",
        "LC": "465",
        "VC": "467",
        "VG": "468",
        "BB": "469",
        "MS": "470",
        "TT": "472",
        "GD": "473",
        "AW": "474",
        "AN": "478",
        "CO": "480",
        "VE": "484",
        "GY": "488",
        "SR": "492",
        "GF": "496",
        "EC": "500",
        "PE": "504",
        "BR": "508",
        "CL": "512",
        "BO": "516",
        "PY": "520",
        "UY": "524",
        "AR": "528",
        "FK": "529",
        "CY": "600",
        "LB": "604",
        "SY": "608",
        "IQ": "612",
        "IR": "616",
        "IL": "624",
        "GZ": "625",
        "JO": "628",
        "SA": "632",
        "KW": "636",
        "BH": "640",
        "QA": "644",
        "AE": "647",
        "OM": "649",
        "YE": "653",
        "AF": "660",
        "PK": "662",
        "IN": "664",
        "BD": "666",
        "MV": "667",
        "LK": "669",
        "NP": "672",
        "BT": "675",
        "MM": "676",
        "TH": "680",
        "LA": "684",
        "VN": "690",
        "KH": "696",
        "ID": "700",
        "MY": "701",
        "BN": "703",
        "SG": "706",
        "PH": "708",
        "MN": "716",
        "CN": "720",
        "KP": "724",
        "KR": "728",
        "JP": "732",
        "TW": "736",
        "HK": "740",
        "MO": "743",
        "AU": "800",
        "PG": "801",
        "OA": "802",
        "NR": "803",
        "NZ": "804",
        "SB": "806",
        "TV": "807",
        "NC": "809",
        "OC": "810",
        "WF": "811",
        "KI": "812",
        "PN": "813",
        "CK": "814",
        "FJ": "815",
        "VU": "816",
        "TO": "817",
        "WS": "819",
        "MP": "820",
        "PF": "822",
        "FM": "823",
        "MH": "824",
        "PR": "890",
        "XX": "891"
    }
    # Default to "000" or any placeholder if the iso_code_sap isn't in the dictionary
    return country_mapping.get(iso_code_sap.upper().strip(), "000")

def get_state_code(state):
    state_mapping = {
    "In Transit": "TRAN",
    "ROLLED": "ROLL",
    "Transit": "TRAN",
    "FURNACE": "FURN",
    "Discharged": "DISC",
    "Charged": "CHAR",
    "Tip": " TIP",
    "Lift off": "LFOF"
}

    return state_mapping.get(state, " "*4)  # Default to ' ' if not found


def SRM_COHTRAN8(id, db_session):
        order_code = '0000142377'
        target_oi = db_session.query(Order.id,Order.work_order,Order.order_category,Order.order_export_type,Order.customer_code,Order.customer_po_number,Order.created_at,Order.business_order_code,
                                     Order.destination_country,Order.carriage_terms,Order.mode_of_delivery,
                                     OrderItem.order_id, OrderItem.rolling_code, OrderItem.delivery_date,OrderItem.product_dim1,
                                     OrderItem.product_code, OrderItem.quality_code,  OrderItem.rolling_code,
                                     OrderItem.tonnage, OrderItem.tonnage_tolerance_min_percent,OrderItem.spec_code, 
                                     OrderItem.product_dim3,OrderItem.tonnage_tolerance_max_percent,
                                     OrderItem.general_remark_1,OrderItem.general_remark_2,OrderItem.general_remark_3,OrderItem.general_remark_4).join(OrderItem, OrderItem.order_id == Order.id).filter(Order.order_code == order_code).first()


        # print(target_oi)
        db_session.commit()

        word_no = str(target_oi.work_order).strip()
        order_export_type = (target_oi.order_export_type).strip()
        acct_code = str(target_oi.business_order_code).strip()
         
        customer_po_number = str(target_oi.customer_po_number).ljust(24) if target_oi.customer_po_number else " ".ljust(24)
        customer_po_number_abb = str(target_oi.customer_po_number).ljust(18) if target_oi.customer_po_number else " ".ljust(18)
        order_type = '1' if target_oi.order_category == None else target_oi.order_category
        created_at = target_oi.created_at.strftime('%d/%m/%y')
        destination_country = str(get_country_code(target_oi.destination_country)).ljust(3)
        # sect_no always set 001
        roll_weekyear = rollingweekyear(target_oi.rolling_code)
        prog_wgt = str(target_oi.tonnage).zfill(4) if target_oi.tonnage else "0".zfill(4)
        order_prog_wgt_min = " "*4 if target_oi.tonnage_tolerance_min_percent is None else target_oi.tonnage_tolerance_min_percent
        order_prog_wgt_max = " "*4 if target_oi.tonnage_tolerance_max_percent is None else target_oi.tonnage_tolerance_max_percent
        #roll_tol_minus  roll_tol_plus set default ' ' *4
        del_suf='10'
        inv_suf='01'
        delivery_method = get_transport_code(target_oi.mode_of_delivery)
        # del_reqd always set BY
        delivery_at =target_oi.delivery_date.strftime('%d%m%y')
        reference_number_obsolete = 'SRM99999' if order_export_type == 'X' else ' '*8
        #delivery_method again
        oi_product_code= str(target_oi.product_dim1).zfill(4) if target_oi.product_dim1 else "0".zfill(4)
        # profile always set RD
        spec_code = target_oi.spec_code
        Coh_dim3 = target_oi.product_dim3
        # coil spilt always set 1
        oi_quality_code=str(target_oi.quality_code).zfill(6) if target_oi.quality_code else " ".zfill(6)
        port_L =' '*4
        port_D = ' '*4
        # natt code always set 10
        # motr code always set 1
        # item no always set 001
        word_wgt = str(target_oi.tonnage).zfill(5) if target_oi.tonnage else "0".zfill(5)
        roll_action = '0' 
        generalremark1 =str(target_oi.general_remark_1).ljust(30) if target_oi.general_remark_1 else " ".ljust(30)
        generalremark2=str(target_oi.general_remark_2).ljust(30) if target_oi.general_remark_2 else " ".ljust(30)
        generalremark3=str(target_oi.general_remark_3).ljust(30) if target_oi.general_remark_3 else " ".ljust(30)
        generalremark4=str(target_oi.general_remark_4).ljust(30) if target_oi.general_remark_4 else " ".ljust(30)
        special_instruction = generalremark1 +generalremark2+generalremark3+generalremark4
        compact_code = ' '*4

        #_________tally color fixed to spaces_________
        tally_type = ' '
        tally_color = ' '
        num_tallise = ' '
        tally_posn = ' '
        ind_date = ' '
        ind_rod_size = ' '
        ind_cust_name = ' '
        ind_cast = ' '
        ind_cust_ord = ' '
        ind_cont_c =' '
        ind_spe_name = ' '
        ind_cont_mn = ' '
        ind_word_no =  ' '
        paint_mark_c1 =  ' ' 
        paint_mark_c2 =  ' '
        paint_mark_c3 =  ' '
        paint_mark_o =  ' '
        paint_mark_t =  ' '
        #_________tally color fixed to spaces_________

        rem_code = '   '*3
        label_info = ' '*24*4
        shipping_condition = ' '*50*3
        carriage_terms = get_incoterm_code(target_oi.carriage_terms)
        lc_req = 'N' if order_export_type == 'X' else ' '
        il_req = 'N' if order_export_type == 'X' else ' '
        reprog_ind = ' '
        discount_rsn = '07'
        terms = '503'
        prcd_code = '65'
        prcd_cuurency ='029'
        prcd_conversion = '000011818'
        prcd_units = 'T'
        prcd_price  = '0660000'
        #fixed '  000000000000 0000000'
        week_from = '26'
        year_from = '25'

        content = ('CRZ52' + word_no + order_export_type + acct_code +customer_po_number+
                   order_type+ customer_po_number_abb+created_at+destination_country+'001'+ 
                   roll_weekyear+prog_wgt+order_prog_wgt_min+order_prog_wgt_max+
                   ' '*4 +' '*4+del_suf+inv_suf+ delivery_method+'BY '+delivery_at+
                   reference_number_obsolete+delivery_method+oi_product_code+'RD '+spec_code+
                   Coh_dim3+'1'+oi_quality_code+port_L+port_D+'10'+'1'+'001' + 
                   word_wgt +roll_action+special_instruction+compact_code+tally_type+tally_color+num_tallise+
                   tally_posn+ind_date+ind_rod_size+ind_cust_name+ind_cast+ind_cust_ord+ind_cont_c+
                   ind_spe_name+ind_cont_mn+ind_word_no+paint_mark_c1+paint_mark_c2+paint_mark_c3+
                   paint_mark_o+paint_mark_t+rem_code+label_info+shipping_condition+carriage_terms+lc_req+il_req+reprog_ind+
                   discount_rsn+terms+prcd_code+prcd_cuurency+prcd_conversion+prcd_units+prcd_price+'  000000000000 0000000'*7+
                   '330'+week_from+year_from+'330')
        return content

def BBMSTKTFR(id, db_session):
        semi_code = '78613501'
        target_oi = db_session.query(Semi.location,Semi.semi_status,Semi.location,Semi.created_at,Semi.hold_reason,
        SemiLoad.vehicle_code,SemiLoad.status ,SemiLoad.semi_count ,SemiLoad.semi_load_code,SemiLoad.dispatch_date,SemiLoad.total_weight_ton,
        Cast.cast_code,Cast.ch_c, Cast.ch_si, Cast.ch_mn, Cast.ch_p, Cast.ch_s, Cast.ch_cr, Cast.ch_mo, 
        Cast.ch_ni, Cast.ch_al, Cast.ch_as, Cast.ch_co, Cast.ch_cu, Cast.ch_nb, Cast.ch_sn, Cast.ch_ti,
          Cast.ch_v, Cast.ch_te, Cast.ch_pb, Cast.ch_b, Cast.ch_n, Cast.ch_ca, Cast.ch_sal,
        Cast.ch_bi, Cast.ch_w, Cast.ch_zr, Cast.ch_sb, Cast.ch_zn, Cast.ch_h, Cast.ch_o

        ).join(SemiLoad, SemiLoad.id == Semi.semi_load_id).join(Cast, Cast.id == Semi.cast_id).filter(Semi.semi_code == semi_code).first()
        print(target_oi)


        db_session.commit()

        timestamp = datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f")
        lastprogram = ' '*8
        func_ind = "D" if target_oi.status == 'in transit' else "S"
        SOP_steel_order_number = ' '*24
        WagonId= str(target_oi.vehicle_code).ljust(7) if target_oi.vehicle_code is not None else " ".zfill(7)
        cast_number  = target_oi.cast_code


        bloom_location = 'DEFAULT'

        bloom_state =get_state_code(target_oi.semi_status) 
        bloom_no = str(target_oi.semi_count).zfill(5) if target_oi.semi_count else " ".zfill(5)

        formatted_num = f"{target_oi.total_weight_ton:.2f}"
        # 去掉小数点前的整数部分的补零，确保总共4位
        integer_part, decimal_part = formatted_num.split(".")
        integer_part = integer_part.zfill(4)  # 补零保证4位整数部分
        bloom_weight = f"{integer_part}{decimal_part}"
        print(bloom_weight)

        despatch_reference  = target_oi.semi_load_code
        despatch_date = '2025-02-12'
        despatch_time = '11.15.15'
        rounte = '2'.ljust(2)

        cast_date = (str(((target_oi.created_at).date() - datetime(1899, 12, 31).date()).days)).zfill(9)
        cast_time =  (target_oi.created_at).strftime("%H%M")
        del_ind = 'N'
        date_ind = '0001-01-01'
        est_wgt_ind = "Y" if func_ind == 'S' else "N"
        final_anal_ind = "N" if func_ind == 'S' else "Y"

        #cast chemcial
        c = f"{target_oi.ch_c:.3f}".replace(".", "") if target_oi.ch_c is not None else "0000"
        si = f"{target_oi.ch_si:.3f}".replace(".", "") if target_oi.ch_si is not None else "0000"
        mn = f"{target_oi.ch_mn:.3f}".replace(".", "") if target_oi.ch_mn is not None else "0000"
        p = f"{target_oi.ch_p:.3f}".replace(".", "") if target_oi.ch_p is not None else "0000"
        s = f"{target_oi.ch_s:.3f}".replace(".", "") if target_oi.ch_s is not None else "0000"
        cr = f"{target_oi.ch_cr:.4f}".replace(".", "") if target_oi.ch_cr is not None else "00000"
        mo = f"{target_oi.ch_mo:.4f}".replace(".", "") if target_oi.ch_mo is not None else "00000"
        ni = f"{target_oi.ch_ni:.4f}".replace(".", "") if target_oi.ch_ni is not None else "00000"
        al = f"{target_oi.ch_al:.4f}".replace(".", "") if target_oi.ch_al is not None else "00000"
        chemcial_as = f"{target_oi.ch_as:.4f}".replace(".", "") if target_oi.ch_as is not None else "00000"
        co = f"{target_oi.ch_co:.4f}".replace(".", "") if target_oi.ch_co is not None else "00000"
        cu = f"{target_oi.ch_cu:.4f}".replace(".", "") if target_oi.ch_cu is not None else "00000"
        nb = f"{target_oi.ch_nb:.4f}".replace(".", "") if target_oi.ch_nb is not None else "00000"
        sn = f"{target_oi.ch_sn:.4f}".replace(".", "") if target_oi.ch_sn is not None else "00000"
        ti = f"{target_oi.ch_ti:.4f}".replace(".", "") if target_oi.ch_ti is not None else "00000"
        v = f"{target_oi.ch_v:.4f}".replace(".", "") if target_oi.ch_v is not None else "00000"
        pb = f"{target_oi.ch_pb:.4f}".replace(".", "") if target_oi.ch_pb is not None else "00000"
        b = f"{target_oi.ch_b:.4f}".replace(".", "") if target_oi.ch_b is not None else "00000"
        n = f"{target_oi.ch_n:.4f}".replace(".", "") if target_oi.ch_n is not None else "00000"
        ca = f"{target_oi.ch_ca:.4f}".replace(".", "") if target_oi.ch_ca is not None else "00000"
        sa = f"{target_oi.ch_sal:.5f}".replace(".", "") if target_oi.ch_sal is not None else "000000"
        bi =f"{target_oi.ch_bi:.4f}".replace(".", "") if target_oi.ch_bi is not None else "00000"
        w = f"{target_oi.ch_w:.4f}".replace(".", "") if target_oi.ch_w is not None else "00000"
        zr = f"{target_oi.ch_zr:.4f}".replace(".", "") if target_oi.ch_zr is not None else "00000"
        sb = f"{target_oi.ch_sb:.4f}".replace(".", "") if target_oi.ch_sb is not None else "00000"
        zn = f"{target_oi.ch_zn:.4f}".replace(".", "") if target_oi.ch_zn is not None else "00000"
        h = f"{target_oi.ch_h:.5f}".replace(".", "") if target_oi.ch_h is not None else "000000"
        o= f"{target_oi.ch_o:.5f}".replace(".", "") if target_oi.ch_o is not None else "000000"


        # c = f"{round(target_oi.ch_c,2):.3f}".replace(".", "") if target_oi.ch_c is not None else "0000"
        # si = f"{round(target_oi.ch_si,2):.3f}".replace(".", "") if target_oi.ch_si is not None else "0000"
        # mn = f"{round(target_oi.ch_mn,2):.3f}".replace(".", "") if target_oi.ch_mn is not None else "0000"
        # p = f"{round(target_oi.ch_p,2):.3f}".replace(".", "") if target_oi.ch_p is not None else "0000"
        # s = f"{round(target_oi.ch_s,2):.3f}".replace(".", "") if target_oi.ch_s is not None else "0000"
        # cr = f"{round(target_oi.ch_cr,3):.4f}".replace(".", "") if target_oi.ch_cr is not None else "00000"
        # mo = f"{round(target_oi.ch_mo,3):.4f}".replace(".", "") if target_oi.ch_mo is not None else "00000"
        # ni = f"{round(target_oi.ch_ni,3):.4f}".replace(".", "") if target_oi.ch_ni is not None else "00000"
        # al = f"{round(target_oi.ch_al,3):.4f}".replace(".", "") if target_oi.ch_al is not None else "00000"
        # chemcial_as = f"{round(target_oi.ch_as,3):.4f}".replace(".", "") if target_oi.ch_as is not None else "00000"
        # co = f"{round(target_oi.ch_co,3):.4f}".replace(".", "") if target_oi.ch_co is not None else "00000"
        # cu = f"{round(target_oi.ch_cu,3):.4f}".replace(".", "") if target_oi.ch_cu is not None else "00000"
        # nb = f"{round(target_oi.ch_nb,3):.4f}".replace(".", "") if target_oi.ch_nb is not None else "00000"
        # sn = f"{round(target_oi.ch_sn,3):.4f}".replace(".", "") if target_oi.ch_sn is not None else "00000"
        # ti = f"{round(target_oi.ch_ti,3):.4f}".replace(".", "") if target_oi.ch_ti is not None else "00000"
        # v = f"{round(target_oi.ch_v,3):.4f}".replace(".", "") if target_oi.ch_v is not None else "00000"
        # pb = f"{round(target_oi.ch_pb,3):.4f}".replace(".", "") if target_oi.ch_pb is not None else "00000"
        # b = f"{round(target_oi.ch_b,3):.4f}".replace(".", "") if target_oi.ch_b is not None else "00000"
        # n = f"{round(target_oi.ch_n,3):.4f}".replace(".", "") if target_oi.ch_n is not None else "00000"
        # ca = f"{round(target_oi.ch_ca,3):.4f}".replace(".", "") if target_oi.ch_ca is not None else "00000"
        # sa = f"{round(target_oi.ch_sal,4):.5f}".replace(".", "") if target_oi.ch_sal is not None else "000000"
        # bi =f"{round(target_oi.ch_bi,3):.4f}".replace(".", "") if target_oi.ch_bi is not None else "00000"
        # w = f"{round(target_oi.ch_w,3):.4f}".replace(".", "") if target_oi.ch_w is not None else "00000"
        # zr = f"{round(target_oi.ch_zr,3):.4f}".replace(".", "") if target_oi.ch_zr is not None else "00000"
        # sb = f"{round(target_oi.ch_sb,3):.4f}".replace(".", "") if target_oi.ch_sb is not None else "00000"
        # zn = f"{round(target_oi.ch_zn,3):.4f}".replace(".", "") if target_oi.ch_zn is not None else "00000"
        # h = f"{round(target_oi.ch_h,4):.5f}".replace(".", "") if target_oi.ch_h is not None else "000000"
        # o= f"{round(target_oi.ch_o,4):.5f}".replace(".", "") if target_oi.ch_o is not None else "000000"


        content = (timestamp +lastprogram + func_ind +  SOP_steel_order_number + WagonId + cast_number + bloom_location +
                         bloom_state + bloom_no + bloom_weight + despatch_reference + despatch_date + despatch_time + rounte +
                         cast_date + cast_time + del_ind + date_ind + est_wgt_ind + final_anal_ind +
                         c+si+mn+p+s +cr +mo +ni +al +chemcial_as + co + cu + nb + sn +ti + v + pb +b+n +
                         ca + sa + bi + w +zr +sb + zn +  h +o)
        # content = ''
        print(content)
        return content



def MFSO2SOP(id, db_session):
        # semi_id = '38518'
        # target_oi = db_session.query(Semi.semi_type,SemiLoad.vehicle_code).join(SemiLoad, SemiLoad.id == Semi.semi_load_id).filter(Semi.id == semi_id).first()
        # print(target_oi)
  
        action = 'A'
        steel_ordernumber ='SRM-4581' 
        supplier_code = 'A5'
        oi_quality_code=str(target_oi.quality_code).zfill(6) if target_oi.quality_code else "".zfill(6)
        size = '283'
        delivery_at =target_oi.delivery_date.strftime('%d/%m/%y')
        leng = 'A'
        length_min = '08000'
        length_max = '08200'
        ref = 'W'
        prog_wgt = str(target_oi.tonnage).zfill(4) if target_oi.tonnage else "".zfill(4)
        prog_pnt = '01'
        primt_ind = ''
        fso_no = '6000'
        associated_junction_order = ''*8
        associated_divert_order = ''*8
        associated_misfit_order = ''*8

        content = (action + steel_ordernumber +supplier_code+oi_quality_code+size+
        delivery_at + leng + length_min+length_max+ref+prog_wgt+prog_pnt+
        primt_ind+fso_no+associated_junction_order+associated_divert_order+associated_misfit_order)
        print(content)
        return content