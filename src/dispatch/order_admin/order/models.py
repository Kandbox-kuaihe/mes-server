from typing import List, Optional
from pydantic import  Field

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase,BaseResponseModel

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Text, text, Index, UniqueConstraint

from dispatch.rolling.rolling_list.models import  RollingRead
from dispatch.mill.models import MillRead
from dispatch.customer.models import CustomerRead

class Order(Base,TimeStampMixin):
    __tablename__ = 'order'
    id = Column(BigInteger, primary_key=True,autoincrement=True)

    plant_id = Column(BigInteger, ForeignKey("mill.id"), nullable=True, )
    plant = relationship("Mill", backref="mill_order1")

    order_code = Column(String, unique=False, nullable=False)
    sap_order_code = Column(String, unique=True, nullable=False)
    order_export_type = Column(String,  nullable=True,comment="H = Home, E = Export")
    order_category = Column(String,  nullable=True,comment="'1' - Prestigious Projects, '2' - ROW and EEC Fabricator, '3' - Home Fabricators, '4' - ROW Stock Holders, '5' - Home and EEC Stockholder")
    type_of_order = Column(Integer,  comment="1=Unknown, 2=Fabricator, 3=Project, 4=UK Stockist, 5=ROW Stockholder", nullable=False)
    business_order_code = Column(String, nullable=True)
    customer_code = Column(String,  nullable=True,comment="Maps to 'customer number'")
    coh_no = Column(Integer)
    year = Column(Integer)

    customer_id = Column(BigInteger, ForeignKey("customer.id"))
    customer = relationship("Customer", backref="customer_order")

    customer_short_name = Column(String, nullable=True,)
    customer_full_name = Column(String, nullable=True,)
    customer_group = Column(String, nullable=True, comment="Reserved")
    address_line_1 = Column(String, nullable=True,)
    address_line_2 = Column(String, nullable=True,)
    address_line_3 = Column(String, nullable=True,)
    address_line_4 = Column(String, nullable=True,)
    address_line_5 = Column(String, nullable=True,)
    section_order_category = Column(String, nullable=True,)
    customer_credit_worthiness = Column(String,  nullable=True,comment="'Y'=Creditworthy, 'N'=Not Creditworthy")
    label_data = Column(String, nullable=True,)
    contract = Column(String, nullable=True,)
    customer_po_number = Column(String, nullable=True,)
    carriage_terms = Column(String, nullable=True, comment="Carriage terms, e.g., Incoterms for export")
    incoterms_location = Column(String, nullable=True,)
    payment_terms = Column(String, nullable=True,)
    mode_of_delivery = Column(String, nullable=True,)
    delivery_note = Column(String, nullable=True,)
    delivery_address_id = Column(String, nullable=True,)
    destination_country = Column(String, nullable=True,)
    job_scheme_name = Column(String, nullable=True, comment="Reserved")
    general_remark_1 = Column(String, nullable=True,)
    general_remark_2 = Column(String, nullable=True,)
    general_remark_3 = Column(String, nullable=True,)
    general_remark_4 = Column(String, nullable=True,)
    copies_of_test_certificate = Column(String, nullable=True,)
    transport_mode = Column(String, nullable=True,)
    ship_to_customer_number = Column(String, nullable=True,)
    test_certificate_customer_number = Column(String, nullable=True,)
    sales_order_unit = Column(String, nullable=True, comment="Reserved for SAP data")
    sales_division = Column(String,  nullable=True,comment="(Sales area data)")
    distribution_channel = Column(String, nullable=True, comment="(Sales area data)")
    sales_organization = Column(String,  nullable=True,comment="(Sales area data)")
    order_reason = Column(String, nullable=True, comment="SAP Order Reason")
    order_note = Column(String, nullable=True)
    outside_inspection_required_flag = Column(String, nullable=True)
    sap_xml = Column(Text, nullable=True)
    xml_file_name = Column(String)
    work_order = Column(String)
    customer_rg = Column(String)
    customer_we = Column(String)


    customer_code_zt = Column(String,  nullable=True,comment="Maps to 'customer number'") # add the decoding when recieved
    customer_short_name_zt = Column(String, nullable=True,)# add the decoding when recieved
    customer_full_name_zt = Column(String, nullable=True,)# add the decoding when recieved
    address_line_1_zt = Column(String, nullable=True,)# add the decoding when recieved
    address_line_2_zt = Column(String, nullable=True,)# add the decoding when recieved
    address_line_3_zt = Column(String, nullable=True,)# add the decoding when recieved
    address_line_4_zt = Column(String, nullable=True,)# add the decoding when recieved
    address_line_5_zt = Column(String, nullable=True,)# add the decoding when recievedcccddddcdd
    vsart = Column(String)

    replenish = Column(String, default='N', comment="'Y'=ZIP exists, 'N'=ZIP does not exists")

    doc_no = Column(String, nullable=True)

    sections_seq = Column(BigInteger)
    rails_seq = Column(BigInteger)
    profile_seq = Column(BigInteger)
    rd_seq = Column(BigInteger)
    semi_seq = Column(BigInteger)
    billet_seq = Column(BigInteger)

    
    search_vector = Column(
        TSVectorType(
            "order_code",
            "customer_short_name",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            weights={
                "order_code": "A",
                "customer_short_name": "B",
                "address_line_1": "C",
                "address_line_2": "C",
                "address_line_3": "C",
            },
        )
    )

    __table_args__ = (
        UniqueConstraint( 'sap_order_code', name='unique_sap_order_code'),
        UniqueConstraint( 'order_code', 'year', name='unique_order_code_year'),
        UniqueConstraint( 'business_order_code', name='unique_business_code'),
        UniqueConstraint( 'coh_no', 'year', name='unique_coh_code_year'),
        Index('idx_order_active_updated', 'updated_at', postgresql_where=(text("is_deleted IS NULL OR is_deleted = 0"))),
    )
    
    
class OrderBase(BaseResponseModel):
    order_code: str
    sap_order_code: Optional[str] = None
    order_export_type: Optional[str] = None
    # Field(None, description="H = Home, E = Export")
    order_category: Optional[str] =None  # Field(None, description="'1' - Prestigious Projects, '2' - ROW and EEC Fabricator, '3' - Home Fabricators, '4' - ROW Stock Holders, '5' - Home and EEC Stockholder")
    type_of_order: int  # Field(None, description="1=Unknown, 2=Fabricator, 3=Project, 4=UK Stockist, 5=ROW Stockholder")
    business_order_code: Optional[str] = None
    coh_no: Optional[int] = None
    year: Optional[int] = None
    customer_code: Optional[str] = None  #Field(None, description="Maps to 'customer number'")
    customer_id: Optional[int] = None
    customer_short_name: Optional[str] = None
    customer_full_name: Optional[str] = None
    customer_group: Optional[str] =None  # Field(None, description="Reserved")
    work_order: Optional[str]=None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    address_line_4: Optional[str] = None
    address_line_5: Optional[str] = None
    section_order_category: Optional[str] = None
    customer_credit_worthiness: Optional[str] =None  # Field(None, description="'Y'=Creditworthy, 'N'=Not Creditworthy")
    label_data: Optional[str] = None
    contract: Optional[str] = None
    customer_po_number: Optional[str] = None
    carriage_terms: Optional[str] = None  #Field(None, description="Carriage terms, e.g., Incoterms for export")
    incoterms_location: Optional[str] = None
    payment_terms: Optional[str] = None
    mode_of_delivery: Optional[str] = None
    delivery_note: Optional[str] = None
    delivery_address_id: Optional[str] = None
    destination_country: Optional[str] = None
    job_scheme_name: Optional[str] = None  #Field(None, description="Reserved")
    general_remark_1: Optional[str] = None
    general_remark_2: Optional[str] = None
    general_remark_3: Optional[str] = None
    general_remark_4: Optional[str] = None
    copies_of_test_certificate: Optional[str] = None
    transport_mode: Optional[str] = None
    ship_to_customer_number: Optional[str] = None
    test_certificate_customer_number: Optional[str] = None
    sales_order_unit: Optional[str] =None  # Field(None, description="Reserved for SAP data")
    sales_division: Optional[str] =None  # Field(None, description="(Sales area data)")
    distribution_channel: Optional[str] =None  # Field(None, description="(Sales area data)")
    sales_organization: Optional[str] = None  #Field(None, description="(Sales area data)")
    order_reason: Optional[str] = None  #Field(None, description="SAP Order Reason")
    order_note: Optional[str] = None
    outside_inspection_required_flag: Optional[str] = None
    # sap_xml: Optional[str] = None #
    customer_code_zt: Optional[str] = None
    customer_short_name_zt: Optional[str] = None
    customer_full_name_zt: Optional[str] = None
    address_line_1_zt: Optional[str] = None
    address_line_2_zt: Optional[str] = None
    address_line_3_zt: Optional[str] = None
    address_line_4_zt: Optional[str] = None
    address_line_5_zt: Optional[str] = None
    plant_id:Optional[int]= None

    vsart: Optional[str] = None
    customer_rg: Optional[str] = None
    customer_we: Optional[str] = None
    replenish: Optional[str] = None
    doc_no: Optional[str] = None

    sections_seq: Optional[int] = None
    rails_seq: Optional[int] = None
    profile_seq: Optional[int] = None
    rd_seq: Optional[int] = None
    semi_seq: Optional[int] = None
    billet_seq: Optional[int] = None

    



class OrderCreate(OrderBase):
    # sap_xml: Optional[str] = None
    xml_file_name: Optional[str] = None

class OrderUpdate(OrderBase):
    pass

class OrderRemarkBase(DispatchBase):
    identifier: Optional[str] = None
    text: Optional[str] = None
    type: Optional[str] = None

class OrderRead(OrderBase,BaseResponseModel):
    id: int
    plant:Optional[MillRead]= None
    customer: Optional[CustomerRead] = None
    order_remarks: List[OrderRemarkBase] = []


class OrderPagination(DispatchBase):
    total: int
    items: List[OrderRead] = []
    itemsPerPage: int
    page : int