import re

def try_int(s: str | None) -> int | None:
    try:
        return int(s)
    except (ValueError, TypeError):
        return None

def try_float(s: str | None) -> float | None:
    try:
        return float(s)
    except (ValueError, TypeError):
        return None

def try_int_num(a) -> int:
    try:
        return int(a)
    except Exception:
        return 0

def try_float_num(a) -> float:
    try:
        return float(a)
    except Exception:
        return 0.0

def try_str(a) -> str:
    try:
        return str(a) if a else ""
    except (ValueError, TypeError):
        return ""

def split_number_and_letters(s: str) -> tuple[str, str] | None:
    match = re.match(r'(\d+)([A-Za-z].*)', s)
    if match:
        return match.group(1), match.group(2)
    return None

def format_float(s: str) -> float | int:
    try:
        num = float(s)
        if num == int(num):
            return int(num)
        else:
            return num
    except (ValueError, TypeError):
        return None