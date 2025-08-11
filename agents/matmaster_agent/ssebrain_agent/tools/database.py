import json
import re
import requests
from typing import Dict, Optional, List
# from . import polymer_db_constants as polymer
# from . import electrolyte_db_constants as electrolyte
from . import solid_electrolyte_db_constants as solid_electrolyte
from pprint import pprint


class DatabaseManager:
    """
    A manager for database operations.
    """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.table_url = "https://db-core.dp.tech/api/common_db/v1/table"
        self.query_url = "https://db-core.dp.tech/api/common_db/v1/common_data/list"
        self.get_headers = {
            'X-User-Id': '14962',
            'X-Org-Id': '3962',
        }
        self.query_headers = {
            'X-User-Id': '14962',
            'X-Org-Id': '3962',
            'Content-Type': 'application/json'
        }

        if self.db_name == 'solid_electrolyte_db':
            tables = solid_electrolyte.SOLID_ELECTROLYTE_DB_TABLES
        else:
            raise ValueError(f'Database name {self.db_name} not supported!')

        # get the table names
        self.paper_text_table = tables.get('paper_text_table', None)
        self.paper_figure_table = tables.get('paper_figure_table', None)
        self.field_info_table = tables.get('field_info_table', None)

        # get the table fields
        self.table_schema = {}
        for table in tables['tables']:
            table_name = table.get('table_name', '')
            table_fields = self.get_table_fields(table_name)
            if 'error' in table_fields:
                table_fields = {'fields': [],}
            table.update(table_fields)
            if not table.get('primary_fields', None):
                table['primary_fields'] = table['fields']
            self.table_schema[table_name] = table

    def get_table_fields(self, table_name: str):
        """
        Get the fields of a table
        Args:
            table_name: the name of the table
        Returns:
            A dictionary containing the fields of the table, {'fields': [field_name1, field_name2, ...]}
        """
        if self.db_name == "electrolyte_db" or self.db_name == "polymer_db":
            raw_table_name = self.field_info_table
            filters = {
                "type": 1,
                "field": "table AK",
                "operator": "eq",
                "value": table_name,
            }
            payload = json.dumps(
                {
                    'userId': 14962,
                    'tableAk': raw_table_name,
                    'filters': filters,
                    'page': 1,
                    'pageSize': 50,
                }
            )
            response = requests.request("POST", self.query_url, headers=self.query_headers, data=payload)
            result = json.loads(response.text)
            fields = []
            primary_fields = []
            for item in result['data']['list']:
                fields.append(item['field'])
                if 'note' in item and 'primary' in item['note']:
                    primary_fields.append(item['field'])
            return {'fields': fields, 'primary_fields': primary_fields}

        params = {
            'tableAk': table_name
        }
        response = requests.get(self.table_url, headers=self.get_headers, params=params)
        res = json.loads(response.text)
        if res['code'] != 0:
            return {'error': response.text}
        if res['data']['fields'] is None or len(res['data']['fields']) == 0:
            return {'error': f'No fields found in table {table_name}'}
        fields = set()
        for field in res['data']['fields']:
            fields.add(field['name'])
        return {'fields': list(fields)}

    def init_get_table_field_info(self):
        """instantiate the get_table_field_info function tool"""
        url = self.table_url
        headers = self.get_headers

        def get_table_field_info(table_name: str, field_name: str) -> dict:
            """
            Get the info of a field in a table
            Args:
                table_name: the name of the table
                field_name: the name of the field
            Returns:
                A dictionary containing the info of the field, {'field_info': {field_name: field_info}}
            """
            if self.db_name == "solid_electrolyte_db":
                raw_table_name = solid_electrolyte.TABLE_FILED_INFO_NAME
                filters = {
                    "type": 1,
                    "field": "table AK",
                    "operator": "eq",
                    "value": table_name  # 注意：如果table_name是字符串，json.dumps会自动加引号
                }
                payload = json.dumps(
                    {
                        'userId': 14962,
                        'tableAk': raw_table_name,
                        'filters': filters,
                        'page': 1,
                        'pageSize': 50,
                    }
                )
                response = requests.request("POST", self.query_url, headers=self.query_headers, data=payload)
                result = json.loads(response.text)
                
                # Check if the response is valid
                if result.get('code') != 0:
                    return {'error': f"Database query failed: {result.get('message', 'Unknown error')}"}
                
                if not result.get('data') or not result['data'].get('list'):
                    return {'error': f"No field information found for table {table_name}"}
                
                fields_info = {}
                for item in result['data']['list']:
                    fields_info[item['field']] = {'field': item['field'], 'type': item['type'], 'description': item['description'],
                                'example': item.get('example', None), 'note': item.get('note', None)}
                return {'field_info': fields_info.get(field_name, {})}

            params = {
                'tableAk': table_name
            }
            response = requests.get(url, headers=headers, params=params)
            res = json.loads(response.text)

            fields_info = {}
            if res['code'] != 0:
                return {'error': response.text}
            if res['data']['fields'] is None or len(res['data']['fields']) == 0:
                return {'error': f'No fields found in table {table_name}'}
            for field in res['data']['fields']:
                fields_info[field['name']] = field
            if field_name not in fields_info:
                return {'error': f'Field {field_name} not found in table {table_name}'}
            return {'field_info': fields_info.get(field_name, {})}

        return get_table_field_info

    def init_query_table(self):
        """instantiate the query_table function tool"""
        url = self.query_url
        headers = self.query_headers

        def query_table(table_name: str, filters_json: str, selected_fields: Optional[List[str]] = None,
                        page: Optional[int] = 1, page_size: Optional[int] = 50) -> dict:
            """
            Query the table
            Args:
                table_name: the name of the table
                filters_json: A JSON formatted string representing the query conditions. IMPORTANT: You must construct the dictionary structure as a valid JSON string.
                The dictionary structure of the filters_json is as follows:
                {
                    'type': 2,
                    'groupOperator': 'and',
                    'sub': [
                        {'type': 1, 'field': 'polymer_type', 'operator': 'like', 'value': 'polyimide'},
                        {'type': 2, 'groupOperator': 'or', 'sub': [
                            {'type': 1, 'field': 'glass_transition_temperature', 'operator': 'lt', 'value': 400},
                        ]}
                    ]
                }
                selected_fields: the fields to include in the result, if None, return all fields
                page: the page number of the query, default is 1
                page_size: the page size of the query, default is 50

            Returns:
                A dictionary containing the result of the query, {'result': [row1, row2, ...], 'row_count': row_count, 'papers': [doi1, doi2, ...], 'paper_count': paper_count}
            """

            def to_snake_case(name):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

            try:
                # First, parse the JSON string back into a Python dictionary
                filters = json.loads(filters_json)
            except json.JSONDecodeError as e:
                return {"error": f"Invalid JSON in filters_json parameter: {e}"}

            if selected_fields is None:
                selected_fields = self.table_schema.get(table_name, {}).get('primary_fields', None)
            
            # Ensure DOI is always included in selected_fields if the table has it
            table_fields = self.table_schema.get(table_name, {}).get('fields', [])
            if 'doi' in table_fields and selected_fields is not None:
                if 'doi' not in selected_fields:
                    selected_fields = selected_fields + ['doi']
                    print(f"Added 'doi' to selected_fields for table {table_name}")
            elif 'DOI' in table_fields and selected_fields is not None:
                if 'DOI' not in selected_fields:
                    selected_fields = selected_fields + ['DOI']  
                    print(f"Added 'DOI' to selected_fields for table {table_name}")
            
            print(f"Final selected_fields: {selected_fields}")
            
            payload = json.dumps(
                {
                    'userId': 14962,
                    'tableAk': table_name,
                    'filters': filters,
                    'selectedFields': selected_fields,
                    'page': page,
                    'pageSize': page_size,
                }
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            result = json.loads(response.text)
            if result['code'] != 0:
                # print(result)
                return {'error': response.text, 'row_count': 0, 'papers': [], 'paper_count': 0}
            if result['data']['list'] is None or len(result['data']['list']) == 0:
                # print(result)
                return {'error': 'No data found!', 'row_count': 0, 'papers': [], 'paper_count': 0}
            rows = []
            for item in result['data']['list']:
                if table_name == "polym00":
                    converted_item = {to_snake_case(key): value for key, value in item.items()}
                    rows.append({key: value for key, value in converted_item.items() if key in selected_fields})
                else:
                    rows.append({key: value for key, value in item.items() if key in selected_fields})
            dois = list(set([item['doi'] for item in result['data']['list'] if 'doi' in item]))
            return {'result': rows, 'row_count': len(result['data']['list']), 'papers': dois, 'paper_count': len(dois)}

        return query_table

    def init_fetch_paper_content(self):
        """instantiate the fetch_paper_content function tool"""
        tables = self.table_schema
        text_table_name = self.paper_text_table
        figure_table_name = self.paper_figure_table
        query_table = self.init_query_table()

        def fetch_paper_content(paper_doi: str) -> dict:
            """
            Fetch the full content of a paper by its DOI
            Args:
                paper_doi: The DOI of the paper to fetch
            Returns:
                A dictionary containing the paper content with keys 'main_txt' and 'figures'
            """
            print(f"paper_doi:{paper_doi}")
            # get paper text
            if text_table_name is None:
                print("Error: text_table_name is None")
                return {'error': 'No text table configured', 'main_txt': '', 'figures': None}
            
            fields = tables.get(text_table_name, {}).get('primary_fields', None)
            print(f"Text table: {text_table_name}, fields: {fields}")
            
            filters_json = json.dumps({'type': 1, 'field': 'doi', 'operator': 'in', 'value': [paper_doi]})
            print(f"Query filters: {filters_json}")
            
            result = query_table(text_table_name, filters_json, fields, page=1, page_size=50)
            print(f"Text query result: {result}")
            
            full_text = None
            if result.get('result', None) and len(result['result']) > 0:
                full_text = result['result'][0].get('main_txt')
                if full_text is None:
                    full_text = result['result'][0].get('main_text', '')
                print(f"Retrieved text length: {len(full_text) if full_text else 0}")
            else:
                print("No text results found")
                if 'error' in result:
                    print(f"Query error: {result['error']}")

            # get paper figures
            if figure_table_name is None:
                print("Warning: figure_table_name is None")
                return {'main_txt': full_text, 'figures': None}
            fields = tables.get(figure_table_name, {}).get('primary_fields', None)
            filters_json = json.dumps({'type': 1, 'field': 'doi', 'operator': 'in', 'value': [paper_doi]})
            result = query_table(figure_table_name, filters_json, fields, page=1, page_size=50)
            figures = None
            if result.get('result', None) and len(result['result']) > 0:
                figures = result['result']

            if full_text is None and figures is None:
                error_msg = 'No text or figure data found!'
                print(f"Final result: {error_msg}")
                return {'error': error_msg, 'tool': 'fetch_paper_content', 'main_txt': '', 'figures': None}
            
            final_result = {'main_txt': full_text, 'figures': figures}
            print(f"Final result keys: {final_result.keys()}")
            print(f"Final text length: {len(full_text) if full_text else 0}")
            return final_result

        return fetch_paper_content
