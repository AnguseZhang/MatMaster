import json


def is_json(json_str):
    try:
        json.loads(json_str)
    except BaseException:
        return False
    return True
