def parse_str(string, start, end, res_len):
    try:
        # 确保 start 和 end 在合理范围内
        if start < 0:
            start = 0
        if end > len(string):
            end = len(string)
        if start >= end:  # 防止 start > end
            return " " * res_len  # 返回填充空格

        res = string[start:end]

        # 判断是否是数值（允许负数和小数）
        if res.replace(".", "", 1).isdigit() or (res.startswith("-") and res[1:].replace(".", "", 1).isdigit()):
            return res.zfill(res_len)  # 数值左补0
        else:
            return res.ljust(res_len)  # 字符串右补空格

    except Exception as e:
        print(f'parse_str error: {string}, start: {start}, end: {end}, res_len: {res_len}')
        return " " * res_len  # 返回填充空格


def build_str(string, res_len=None):
    try:
        if not string or string == "None": return " " * max(0, res_len)
        string = str(string)
        if res_len == 0:
            return ""  # res_len 为 0 返回空字符串
        if not res_len:
            return string

        # string = string.strip()
        if string.replace(".", "", 1).isdigit() or (string.startswith("-") and string[1:].replace(".", "", 1).isdigit()):
            return string.zfill(res_len)[-res_len:]  # 数值左侧补 0，进行截断
        else:
            return string.ljust(res_len)[:res_len]  # 字符串右侧补空格，进行截断

    except Exception as e:
        print(f'build_str error: {string}, res_len: {res_len}')
        return " " * max(0, res_len)  # 确保不会返回负长度的空格字符串