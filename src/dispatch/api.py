from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from dispatch.area.views import router as area_router
from dispatch.cast.views import router as cast_router
from dispatch.cast_spec.views import router as cast_spec_router
from dispatch.customer.views import router as customer_router
from dispatch.defect_reason.views import router as defect_reason_router
from dispatch.message_admin.message.views import router as message_router
from dispatch.message_admin.message_log.views import router as message_log_router
from dispatch.message_admin.message_server.views import router as message_server_router
from dispatch.message_admin.operation_log.views import router as operation_log_router
from dispatch.mill.views import router as mill_router
from dispatch.bundle_matrix.views import router as bundle_matrix_router
from dispatch.order_admin.order.views import router as order_router
from dispatch.order_admin.order_group.views import router as order_group_router
from dispatch.order_admin.order_item.views import router as order_item_router
from dispatch.org.views import router as orgs_router
from dispatch.product_category.views import router as product_category_router
from dispatch.product_class.views import router as product_class_router
from dispatch.product_type.views import router as product_type_router
from dispatch.product_size.views import router as product_size_router
from dispatch.rolling.rolling_list.views import router as rolling_router
from dispatch.runout_admin.advice.views import router as advice_router
from dispatch.runout_admin.finished_product.views import router as finished_product_router
from dispatch.runout_admin.finished_product_history.views import router as finished_product_history_router
from dispatch.runout_admin.finished_product_load.views import router as finished_product_load_router
from dispatch.runout_admin.holdreason.views import router as holdreason_router
from dispatch.runout_admin.regradereason.views import router as regradereason_router
from dispatch.runout_admin.runout_list.views import router as runout_router
from dispatch.tests_admin.test_list.views import router as test_router
from dispatch.runout_admin.transport.views import router as transport_router
from dispatch.runout_admin.transport_history.views import router as transport_history_router

from dispatch.semi_admin.alternative_semi_size.views import router as alternative_semi_size_router
from dispatch.semi_admin.semi.views import router as semi_router
from dispatch.semi_admin.semi_end_use_manual.views import router as semi_manual_router
from dispatch.semi_admin.semi_load.views import router as semi_load_router
from dispatch.semi_admin.semi_move_history.views import router as semi_history_router
from dispatch.semi_admin.semi_size.views import router as semi_size_router
from dispatch.semi_admin.semi_size_detail.views import router as semi_size_detail_router
from dispatch.semi_admin.semi_hold_reason.views import router as semi_hold_reason_router

from dispatch.shiftAdmin.shift.views import router as shift_router
from dispatch.shiftAdmin.shift_delay.views import router as shift_delay_router
from dispatch.site.views import router as site_router
from dispatch.site_type.views import router as site_type_router
from dispatch.spec_admin.deoxidation.views import router as deoxidation_router
from dispatch.spec_admin.inspector.views import router as inspector_router
from dispatch.spec_admin.remark.views import router as remark_router
from dispatch.spec_admin.sp_formula.views import router as sp_formula_router
from dispatch.spec_admin.sp_obs.views import router as sp_obs_router
from dispatch.spec_admin.sp_various.views import router as sp_various_router
from dispatch.spec_admin.sp_other_test.views import router as sp_other_test_router
from dispatch.spec_admin.spbend.views import router as spbend_router
from dispatch.spec_admin.spcev.views import router as spcev_router
from dispatch.spec_admin.spcevan.views import router as spcevan_router
from dispatch.spec_admin.spcombel.views import router as spcombel_router
from dispatch.spec_admin.spec.views import router as spec_router
from dispatch.spec_admin.spelong.views import router as spelong_router
from dispatch.spec_admin.spimpact.views import router as spimpact_router
from dispatch.spec_admin.spjominy.views import router as spjominy_router
from dispatch.spec_admin.spmainel.views import router as spmainel_router
from dispatch.spec_admin.spmainel_other_element.views import router as spmainel_other_element_router
from dispatch.spec_admin.spmillref.views import router as spmillref_router
from dispatch.spec_admin.spprodan.views import router as spprodan_router
from dispatch.spec_admin.spprodan_other_element.views import router as spprodan_other_element_router
from dispatch.spec_admin.sprem.views import router as sprem_router
from dispatch.spec_admin.spria.views import router as spria_router
from dispatch.spec_admin.spscond.views import router as spscond_router
from dispatch.spec_admin.spsource.views import router as spsource_router
from dispatch.spec_admin.sptcert.views import router as sptcert_router
from dispatch.spec_admin.sptensil.views import router as sptensil_router
from dispatch.spec_admin.spyield.views import router as spyield_router
from dispatch.spec_admin.tolerance.views import router as tolerance_router
from dispatch.spec_admin.tolerance_detail.views import router as tolerance_detail_router
from dispatch.system_admin.auth.service import get_current_user
from dispatch.system_admin.auth.views import auth_router, user_router
from dispatch.system_admin.menu.views import router as menu_router
from dispatch.system_admin.menu_button.views import router as menu_button_router
from dispatch.system_admin.role.views import router as role_router
from dispatch.tests_admin.bend_test_card.views import router as bend_test_card_router
from dispatch.tests_admin.cleanness_test_card.views import router as test_cleanness_router
from dispatch.tests_admin.decarburisation_test_card.views import router as decarburisation_test_card_router
from dispatch.tests_admin.hardness_test_card.views import router as test_hardness_router
from dispatch.tests_admin.impact_test_card.views import router as test_impact_router
from dispatch.tests_admin.product_hydrogen_test_card.views import router as product_hydrogen_test_card_router
from dispatch.tests_admin.product_analysis_card.views import router as product_analysis_card_router
from dispatch.tests_admin.resistivity_test_card.views import router as resistivity_test_card_router
from dispatch.tests_admin.sulphur_test_card.views import router as test_sulphur_router
from dispatch.tests_admin.tensile_test_card.views import router as test_tensile_router
from dispatch.tests_admin.test_chemial.views import router as test_chemial
from dispatch.tests_admin.test_result_chemical.views import router as test_result_chemical_router
from dispatch.tests_admin.test_result_impact.views import router as test_result_impact_router
from dispatch.tests_admin.test_result_tensile.views import router as test_result_tensile_router
from dispatch.tests_admin.test_result_tensile_thickness.views import router as test_result_tensile_thickness_router
from dispatch.tests_admin.test_sample.views import router as test_sample_router
from dispatch.tests_admin.test_msg_tensile.views import router as test_msg_tensile_router
from dispatch.runout_admin.test_coverage.views import router as test_coverage_router
from dispatch.covering_admin.cover_end_use.views import router as corvering_router
from dispatch.covering_admin.required_test_cover.views import router as required_test_cover_router
from dispatch.spec_admin.alt_quality_code.views import router as alt_quality_code_router
from dispatch.rolling.cut_sequence_plan.views import router as cut_sequence_plan_router
from dispatch.semi_admin.stock_level.views import router as semi_stock_router    
from dispatch.runout_admin.finished_product_stock_level.views import router as finished_product_stock_level_router
from dispatch.spec_admin.quality.views import router as quality_router
from dispatch.spec_admin.quality_element.views import router as quality_element_router
from dispatch.spec_admin.quality_other_element.views import router as quality_other_element_router
from dispatch.order_admin.order_remark.views import router as order_remark_router
from dispatch.order_admin.order_item_remark.views import router as order_item_remark_router
from dispatch.tests_admin.test_history.views import router as test_history_router
from dispatch.tests_admin.test_jominy.views import router as test_jominy_router
from dispatch.tests_admin.test_job.views import router as test_job_router

from .config import BASE_ENV, DISPATCH_UI_URL

api_router = APIRouter(default_response_class=JSONResponse)
# WARNING: Don't use this unless you want unauthenticated routes
authenticated_api_router = APIRouter()
unauthenticated_api_router = APIRouter()

##########################################################################
# doc_exposed_api_router
##########################################################################
doc_exposed_api_router = APIRouter()

doc_router = APIRouter()
ping_router = APIRouter()

unauth_view_routers = [
    ("message_server", message_server_router),
    ("auth", auth_router),
    ("docs", doc_router),
    ("ping", ping_router),
]

view_routers = [
    ('advice', advice_router),
    ('transport', transport_router),
    ('transport_history', transport_history_router),
    ("inspector", inspector_router),
    ("holdreason", holdreason_router),
    ("regradereason", regradereason_router),
    ("opreation_log", operation_log_router),
    ("message", message_router),
    ("message_log", message_log_router),
    # ("message_server", message_server_router),
    ("rolling", rolling_router),
    ("role", role_router),
    ("menu", menu_router),
    ("menu_button", menu_button_router),
    ("user", user_router),
    ("orgs", orgs_router),
    # mill
    ("mill", mill_router),
    ("site", site_router),
    ("area", area_router),
    ("site_type", site_type_router),
    #shift
    # shift
    ("shift", shift_router),
    ("shift_delay", shift_delay_router),
    ("defect_reason", defect_reason_router),
    ("bundle_matrix", bundle_matrix_router),
    #
    ("order", order_router),
    ("order_item", order_item_router),
    ("order_group", order_group_router),
    ("order_remark", order_remark_router),
    ("order_item_remark", order_item_remark_router),
    ("semi", semi_router),
    ("semi_load", semi_load_router),
    ("semi_move_history", semi_history_router),
    ("semi_end_use_manual", semi_manual_router),
    ("stock_level",semi_stock_router) ,  
    ("finished_product_stock_level", finished_product_stock_level_router),
    ("alternative_semi_size", alternative_semi_size_router),
    ("semi_size", semi_size_router),
    ("semi_size_detail", semi_size_detail_router),
    ("semi_hold_reason", semi_hold_reason_router),

    ("product_type", product_type_router),
    ("product_category", product_category_router),
    ("product_class", product_class_router),
    ("product_size", product_size_router),
    # test 大类 ， 测试
    ("test", test_router),
    ("test_impact", test_impact_router),
    ("test_cleanness", test_cleanness_router),
    ("test_sulphur", test_sulphur_router),
    ("test_hardness", test_hardness_router),
    ("test_tensile", test_tensile_router),
    ("test_sample", test_sample_router),
    ("test_result_tensile", test_result_tensile_router),
    ("test_result_tensile_thickness", test_result_tensile_thickness_router),
    ("test_result_impact", test_result_impact_router),
    ("test_result_chemical", test_result_chemical_router),
    ("test_coverage", test_coverage_router),
    ("test_msg_tensile", test_msg_tensile_router),
    ("test_jominy", test_jominy_router),
    ("test_job", test_job_router),
    # spec 大类 ， 规格
    ("spec", spec_router),
    ("alt_quality_code", alt_quality_code_router),
    ("spcombel", spcombel_router),
    ("spelong", spelong_router),
    ("spjominy", spjominy_router),
    ("spprodan", spprodan_router),
    ("spria", spria_router),
    ("spsource", spsource_router),
    ("sptensil", sptensil_router),
    ("spcevan", spcevan_router),
    ("spimpact", spimpact_router),
    ("spmainel", spmainel_router),
    ("sprem", sprem_router),
    ("spscond", spscond_router),
    ("sptcert", sptcert_router),
    ("spyield", spyield_router),
    ("spcev", spcev_router),
    ("spmainel_other_element", spmainel_other_element_router),
    ("spprodan_other_element", spprodan_other_element_router),
    ("deoxidation", deoxidation_router),
    ("spbend", spbend_router),
    ("remark", remark_router),
    ("spmillref", spmillref_router),
    ("quality", quality_router),
    ("quality_element", quality_element_router),
    ("quality_other_element", quality_other_element_router),
    # runout
    ("runout", runout_router),
    ("finished_product_load", finished_product_load_router),
    # ("finished_product", finished_product_router),
    ("cover_end_use", corvering_router),
    ("required_test_cover", required_test_cover_router),

    
    
    
    # Cast 大类
    ("cast",cast_router),
    ("cast_spec", cast_spec_router),
    
    ("tolerance", tolerance_router),
    ("tolerance_detail", tolerance_detail_router),

    ("finished_product", finished_product_router),
    ("finished_product_history", finished_product_history_router),
    ("bend_test_card", bend_test_card_router),
    ("decarburisation_test_card", decarburisation_test_card_router),
    ("product_hydrogen_test_card", product_hydrogen_test_card_router),
    ("test_prodan", product_analysis_card_router),
    ("resistivity_test_card", resistivity_test_card_router),
    ("test_chemial", test_chemial),
    
    # customer
    ("customer", customer_router),

    # srsm spec
    ("sp_formula", sp_formula_router),
    ("sp_various", sp_various_router),
    ("sp_obs", sp_obs_router),
    ("sp_other_test", sp_other_test_router),

    ("cut_sequence_plan", cut_sequence_plan_router),
    ("test_history", test_history_router),
]


def include_routers(api_router_param, routers,dependencies = False):
    for route in routers:
        if dependencies:
            api_router_param.include_router(route[1], prefix=f"/{route[0]}", tags=[f"{route[0]}"],dependencies=[Depends(get_current_user)])
        else:
            api_router_param.include_router(route[1], prefix=f"/{route[0]}", tags=[f"{route[0]}"])

# TODO 注意生成doc 文件的时候注释放开
# include_routers(doc_exposed_api_router, view_routers)
# include_routers(doc_exposed_api_router, unauth_view_routers)

# include_routers(authenticated_api_router, view_routers,dependencies = True)
# include_routers(unauthenticated_api_router, unauth_view_routers,dependencies = True)


@doc_router.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="MES API Doc", version="1.0.0", routes=doc_exposed_api_router.routes))


@doc_router.get("/", include_in_schema=False)
async def get_documentation():
    # return get_redoc_html(openapi_url=f"/{BASE_ENV}/api/v1/docs/openapi.json", title=" API Document")
    # DISPATCH_UI_URL 改成前端对应的域名 ，否则打不开doc
    return get_redoc_html(
        openapi_url=f"{DISPATCH_UI_URL}{BASE_ENV}/api/v1/docs/openapi.json",
        title="MES API Document",
        redoc_js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
    )


@ping_router.get("/")
async def ping():
    return {"message": "pong"}

# api_router.include_router(doc_router, prefix="/docs")
# # api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

#
# api_router.routes.extend(authenticated_api_router.routes)
# api_router.routes.extend(unauthenticated_api_router.routes)