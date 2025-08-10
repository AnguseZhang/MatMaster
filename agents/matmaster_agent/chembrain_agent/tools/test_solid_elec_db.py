import json
import requests
import re

from agents.matmaster_agent.chembrain_agent.tools.database import DatabaseManager


def polymer_db_query_table():
    db_manager = DatabaseManager('solid_electrolyte_db')
    print(db_manager.table_schema)
    query_table = db_manager.init_query_table()
    result = query_table(
        table_name="723wm03",
        filters_json=json.dumps({"type": 2, "groupOperator": "and",
                                 "sub": [
                                     # {"type": 1, "field": "Li/Na-system", "operator": "eq", "value": "yes"},
                                     # {"type": 1, "field": "ionicconductivity->value(mS/cm)", "operator": "gt", "value": 1},
                                     # {"type": 1, "field": "ionicconductivity->value(mS/cm)", "operator": "gt",
                                     #  "value": 10},
                                     {'type': 1, 'field': 'dopantformula', 'operator': 'eq', 'value': 'Ga'},
                                     # {"type": 1, "field": "ionicconductivity->temperature(°C)", "operator": "eq", "value": 100},
                                     # {"type": 1, "field": "base name", "operator": "eq",
                                     #  "value": "CaPr2S4"},
                                     # {"type": 1, "field": "ionic conductivity->method", "operator": "eq", "value": "AC impedance"},
                                     # {"type": 1, "field": "solidelectrolyte", "operator": "eq", "value": "yes"}

                                 ]}),
        selected_fields=['doi', 'id', 'ionicconductivity->value(mS/cm)']
    )
    print(result)


def fetch_paper_content(paper_url):
    db_manager = DatabaseManager('solid_electrolyte_db')
    # db_manager = DatabaseManager('electrolyte_db')
    fetch_paper_content = db_manager.init_fetch_paper_content()
    paper_content = fetch_paper_content(paper_url)
    print(paper_content)
    return paper_content



def table_info_filed():
    raw_table_name = "133ef19"
    filters = {
        "type": 1,
        "field": "tableAK",
        "operator": "eq",
        "value": "133ef07"  # 注意：如果table_name是字符串，json.dumps会自动加引号
    }
    payload = json.dumps(
        {
            'userId': 14962,
            'tableAk': raw_table_name,
            'filters': filters,
            'page': 1,
            'pageSize': 100,
        }
    )
    response = requests.request("POST", "https://db-core.dp.tech/api/common_db/v1/common_data/list",
                                headers={
                                    'X-User-Id': '14962',
                                    'X-Org-Id': '3962',
                                    'Content-Type': 'application/json'
                                }, data=payload)
    result = json.loads(response.text)
    print(f"table_filed_info:{result}")
    if result['code'] != 0:
        print(result)
        return {'error': response.text, 'row_count': 0, 'papers': [], 'paper_count': 0}
    if result['data']['list'] is None or len(result['data']['list']) == 0:
        print(result)
        return {'error': 'No data found!', 'row_count': 0, 'papers': [], 'paper_count': 0}
    rows = []

    def to_snake_case(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    res = []
    for item in result['data']['list']:
        res.append({'field':item['field'], 'type': item['type'], 'description': item['description'], 'example': item.get('example', None)})
    print(res)


def get_table_field():
    db_manager = DatabaseManager('electrolyte_db')
    get_table_field_info = db_manager.init_get_table_field_info()
    result = db_manager.get_table_fields(
        table_name="133ef18",
    )
    print(result)


if __name__ == '__main__':
    polymer_db_query_table()
    # fetch_paper_content("10.1002/adfm.202211805")
    # table_info_filed()
    # get_table_field()
