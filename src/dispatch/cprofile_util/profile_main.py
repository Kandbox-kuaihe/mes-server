import cProfile
from functools import wraps
from dispatch.enums import FilePath
import os


def profile_start(output_file=None, enable_profiler=True):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # 如果没有指定 output_file，则使用 {函数名}_result.out
            nonlocal output_file

            if output_file is None:
                output_file = f"{FilePath.CPROFILE_RESULT_PATH.value}{func.__name__}_result.out"

            # 如果 enable_profiler 为 True，才进行性能分析
            if enable_profiler:
                profiler = cProfile.Profile()
                profiler.enable()  # 启动性能分析

                try:
                    result = func(*args, **kwargs)
                finally:
                    profiler.disable()  # 停止性能分析
                    profiler.dump_stats(output_file)  # 保存分析结果到文件
                    print(f"Profile results saved to: {os.path.abspath(output_file)}")
            else:
                result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator
