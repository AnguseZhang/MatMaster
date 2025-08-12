import json


def is_json(json_str):
    try:
        json.loads(json_str)
    except:
        return False
    return True
