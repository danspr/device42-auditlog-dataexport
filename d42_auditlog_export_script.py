import requests
import pandas as pd
import requests.auth
import urllib3
import base64
from datetime import datetime
import json
import ast

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
D42_HOST = "172.16.3.141"
D42_USERNAME = "admin"
D42_PASSWORD = "C0mpn3t!"
D42_API_URL = "https://" + D42_HOST + "/services/data/v1.0/query/"
QUERY_INTERVAL_DAYS = 90
CUSTOM_FIELDS = {
    "1": "Asset Tag"
}


def get_auditlog_data(query):
    credentials = f"{D42_USERNAME}:{D42_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    headers = {
        'Authorization': 'Basic ' + encoded_credentials,
    }

    payload = {
        'output_type': 'json',
        'query': query
    }
    
    try:
        response = requests.post(D42_API_URL, headers=headers, data=payload, verify=False)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error during API request:", e)
        return None
    
def getKeyMapping(key):
    key_mapping = {
        'object_id': 'Device ID',
        'name': 'Device Name',
        'auditlog_pk': 'Log ID',
        'action_date_time': 'Changed Time',
        'origin': 'Origin',
        'user': 'Changed By',
        'changed_fields': 'Changed Fields',
        'type_id': 'type'
    }
    return key_mapping.get(key, key)

def process_changed_fields_details(recordDetails):
    kv_pairs = []
    recordDetails = json.loads(recordDetails)
    for key, value in recordDetails.items():
        display_key = getKeyMapping(key)
        kv_pairs.append(f"{display_key}: {value}")
    return kv_pairs

def process_changed_fields_custom(record):
    formatted_str = record.replace("=>", ":")
    parsed_dict = ast.literal_eval(f"{{{formatted_str}}}")
    result_str = ", ".join(f"{CUSTOM_FIELDS.get(k, k)}: {v}" for k, v in parsed_dict.items())
    return result_str
    
def get_value(row_data, key, default=None):
    return row_data.get(key, default)

def process_changed_fields(cf):
    data = ''
    if isinstance(cf, dict):
        if len(cf) == 1 and 'last_discovered' in cf:
            data = None
        else:
            kv_pairs = []
            for key, value in cf.items():
                if key == 'details':
                    fieldDetail = process_changed_fields_details(value)
                    kv_pairs.append(f"{fieldDetail}")
                elif key == 'custom_fields':
                    fieldDetail = process_changed_fields_custom(value)
                    kv_pairs.append(f"{fieldDetail}")
                else:
                    display_key = getKeyMapping(key)
                    kv_pairs.append(f"{display_key}: {value}")
            data = "\n".join(kv_pairs)
    return data

def process_row_data(rowData, changedFields):
    data = ''
    if(changedFields is not None):
        if isinstance(changedFields, dict):
            kv_pairs = []
            for key, value in changedFields.items():
                if key != 'custom_fields':
                    kv_pairs.append(f"{key}: {get_value(rowData, key)}")
            data = "\n".join(kv_pairs)
    return data

def export_to_excel(data, output_file):
    if isinstance(data, dict) and 'result' in data:
        records = data['result']
    else:
        records = data
    
    df = pd.DataFrame(records)
    try:
        df.to_excel(output_file, index=False)
        print(f"Data exported successfully to '{output_file}'")
    except Exception as e:
        print("Error exporting to Excel:", e)

def getQueryLog():
    query = f"""SELECT a.auditlog_pk, a.object_id, b.name, a.action_date_time, a.origin, a.user, a.row_data as original_data, a.changed_fields
            FROM view_auditlog_v2 a 
            LEFT JOIN view_device_v1 b on a.object_id = b.device_pk 
            WHERE a.type = 'Device' and a.action = 'Update'
            and a.action_date_time::date >= CURRENT_DATE - INTERVAL '{QUERY_INTERVAL_DAYS} days'
            ORDER BY a.action_date_time DESC;"""
    return query;


def main():
    print(getQueryLog())
    response = get_auditlog_data(getQueryLog())
    if response is None:
        print("Failed to retrieve data from the API.")
        return

    data = []
    for item in response:
        changedData = process_changed_fields(item['changed_fields'])
        rowData = process_row_data(item['original_data'], item['changed_fields'])
        if changedData is None:
            continue
        else:
            item['changed_fields'] = changedData
        
        
        if rowData is not None:
            item['original_data'] = rowData
        data.append(item)

    now = datetime.now()
    currentDatetime = now.strftime("%Y-%m-%d_%H.%M.%S")
    fileName = "export/device42_auditlog_export_" + currentDatetime + ".xlsx"
    export_to_excel(data, fileName)

if __name__ == '__main__':
    main()