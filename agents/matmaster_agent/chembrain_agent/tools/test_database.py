from .database import DatabaseManager
import json
from pprint import pprint
import pandas as pd

def test_polymer_db_query_table():
    db_manager = DatabaseManager('polymer_db')
    print(db_manager.table_schema)
    for table in db_manager.table_schema.values():
        print(table)
        print(len(table['fields']))
        print(len(table['primary_fields']))
        print('-'*100)
    query_table = db_manager.init_query_table()
    result = query_table(
        table_name="polym00",
        filters_json=json.dumps({
            "type": 2,
            "groupOperator": "and",
            "sub": [
                {"type": 1, "field": "polymer_type", "operator": "like", "value": "polyimide"},
                {"type": 1, "field": "glass_transition_temperature", "operator": "gt", "value": 450}
            ]
        }),
        selected_fields=["doi", "name", "glass_transition_temperature"],
        page=1,
        page_size=10,
    )
    print(result)


def test_polymer_get_field_info():
    db_manager = DatabaseManager('polymer_db')
    get_table_field_info = db_manager.init_get_table_field_info()
    result = get_table_field_info(
        table_name="polym00",
        field_name="glass_transition_temperature"
    )
    print(result)


def test_polymer_db_fetch_paper_metadata():
    db_manager = DatabaseManager('polymer_db')
    query_table = db_manager.init_query_table()
    result = query_table(
        table_name="690hd00",
        filters_json=json.dumps({
            "type": 1,
            "field": "doi", 
            "operator": "in",
            "value": ['10.1016/j.polymer.2021.123488', '10.1039/d0ra10138a', '10.1002/pol.20200545', '10.1002/pol.20230948', '10.1007/s10965-014-0463-y', '10.1007/s12221-020-1380-9', '10.1007/s10965-015-0726-2', '10.1016/j.reactfunctpolym.2019.05.009', '10.1002/pola.28626', '10.1016/j.polymer.2019.122100', '10.3390/polym10050546', '10.1002/pol.20190233', '10.1016/j.polymer.2018.05.006', '10.1002/app.39324', '10.1007/s10965-014-0424-5', '10.1002/pol.20210156', '10.1007/s10965-019-1930-2', '10.1016/j.polymer.2019.121862', '10.1177/0954008312466278', '10.1021/acsomega.0c05278', '10.1016/j.polymer.2017.03.006', '10.1016/j.polymer.2020.122889', '10.1002/pi.5922', '10.1002/app.45168', '10.1021/acs.macromol.1c01422', '10.1002/app.27540', '10.1016/j.polymer.2020.122482'],
        }),
        selected_fields=["doi", "article_type", "journal_partition"]
    )
    pprint(result)
    return


def test_polymer_db_fetch_paper_content():
    db_manager = DatabaseManager('polymer_db')
    fetch_paper_content = db_manager.init_fetch_paper_content()
    result = fetch_paper_content('10.1016/j.polymer.2019.122100')
    print(result['main_txt'][:100])
    print('-'*100)

def test_electrolyte_db_manager():
    db_manager = DatabaseManager('electrolyte_db')
    pprint(db_manager.table_schema)
    print('-'*100)
    for table in db_manager.table_schema.values():
        print(table)
        print(len(table['fields']))
        print(len(table['primary_fields']))
        print('-'*100)

def test_electrolyte_db_table_field_info():
    db_manager = DatabaseManager('electrolyte_db')
    get_table_field_info = db_manager.init_get_table_field_info()
    result = get_table_field_info(
        table_name="133ef11",
        field_name="figure"
    )
    pprint(result['field_info'])
    print('-'*100)

def test_electrolyte_db_query_table():
    db_manager = DatabaseManager('electrolyte_db')
    query_table = db_manager.init_query_table()
    result = query_table(
        table_name="133ef11",
        filters_json=json.dumps({
            "type": 1,
            "field": "doi", 
            "operator": "in",
            "value": ['10.1002/celc.201901735'],
        }),
    )
    pprint(result['row_count'])
    print('-'*100)

def test_electrolyte_db_fetch_paper_content():
    db_manager = DatabaseManager('electrolyte_db')
    fetch_paper_content = db_manager.init_fetch_paper_content()
    result = fetch_paper_content('10.1002/celc.201800289')
    pprint(result['main_txt'][:100])
    print('-'*100)

def test_solid_electrolyte_db_manager():
    db_manager = DatabaseManager('solid_electrolyte_db')
    pprint(db_manager.table_schema)
    print('-'*100)
    for table in db_manager.table_schema.values():
        print(table)
        print(len(table['fields']))
        print(len(table['primary_fields']))
        print('-'*100)
    
def test_solid_electrolyte_db_query_table():
    db_manager = DatabaseManager('solid_electrolyte_db')
    query_table = db_manager.init_query_table()
    result = query_table(
        table_name="723wm03",
        selected_fields=["doi", "states", "theoreticaldensity(g/cm^3)"],
        filters_json=json.dumps({
            "type": 1,
            "field": "doi",
            "operator": "eq",
            "value": '10.1007/s11581-015-1529-5',
        }),
    )
    pprint(result)
    print('-'*100)

def test_solid_electrolyte_db_table_field_info():
    db_manager = DatabaseManager('solid_electrolyte_db')
    get_table_field_info = db_manager.init_get_table_field_info()
    result = get_table_field_info(
        table_name="723wm03",
        field_name="states"
    )
    pprint(result['field_info'])
    print('-'*100)

def test_solid_electrolyte_db_fetch_paper_content():
    db_manager = DatabaseManager('solid_electrolyte_db')
    fetch_paper_content = db_manager.init_fetch_paper_content()
    result = fetch_paper_content('10.1007/s11581-015-1529-5')
    pprint(result['main_txt'][:100])
    print('-'*100)

if __name__ == "__main__":
    test_polymer_db_query_table()
    test_polymer_db_fetch_paper_content()
    test_polymer_get_field_info()
    test_polymer_db_fetch_paper_metadata()

    test_electrolyte_db_manager()
    test_electrolyte_db_table_field_info()
    test_electrolyte_db_query_table()
    test_electrolyte_db_fetch_paper_content()

    test_solid_electrolyte_db_manager()
    test_solid_electrolyte_db_query_table()
    test_solid_electrolyte_db_table_field_info()
    test_solid_electrolyte_db_fetch_paper_content()