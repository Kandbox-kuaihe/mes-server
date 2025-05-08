import pytest
from openpyxl import Workbook
from datetime import datetime

## pytest --verbose -p  pytest_get
@pytest.hookimpl(hookwrapper=True)
def pytest_collection_finish(session):
    outcome = yield
    # 获取所有收集到的测试用例
    items = session.items
    # 创建一个新的 Excel 工作簿
    wb = Workbook()
    ws = wb.active
    # 用于统计每个文件的测试用例数量
    file_test_count = {}
    # 用于统计所有测试用例的总数
    total_test_count = 0

    # 先遍历一次统计每个文件的测试用例数量和所有测试用例总数
    for item in items:
        test_path = item.location[0]
        if test_path in file_test_count:
            file_test_count[test_path] += 1
        else:
            file_test_count[test_path] = 1
        total_test_count += 1

    # 设置表头
    ws.append(['汇总', '测试用例文件路径', '测试用例名称', '测试用例描述'])

    # 写入测试用例信息
    for item in items:
        # 获取测试用例名称
        test_name = item.name
        # 获取测试用例文件路径
        test_path = item.location[0]
        # 获取测试用例描述
        test_doc = item.obj.__doc__ if item.obj.__doc__ else ""

        # 获取该文件的测试用例数量
        count = file_test_count[test_path]

        # 将测试用例信息写入 Excel 表格，调整列顺序
        ws.append([count, test_path, test_name, test_doc])

    # 在最后一行添加所有测试用例数量的汇总信息
    ws.append([total_test_count, '全部测试用例总数', '', ''])

    current_date = datetime.now().strftime("%Y%m%d")
    # 生成包含日期的文件名
    file_name = f'test_cases_{current_date}.xlsx'
    # 保存 Excel 文件
    wb.save(file_name)
    