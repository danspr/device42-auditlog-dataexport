import requests
import pandas as pd
import requests.auth
import urllib3
import base64
from datetime import datetime
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
D42_HOST = "172.16.3.141"
D42_USERNAME = "admin"
D42_PASSWORD = "C0mpn3t!"
D42_API_URL = "https://" + D42_HOST + "/services/data/v1.0/query/"
QUERY_INTERVAL_DAYS = 60


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
        'type_id': 'type'
    }
    return key_mapping.get(key, key)

def process_changed_fields(record):
    cf = record.get('changed_fields')
    if cf is None:
        return record
    if isinstance(cf, dict):
        if len(cf) == 1 and 'last_discovered' in cf:
            record['changed_fields'] = None
        else:
            kv_pairs = []
            for key, value in cf.items():
                display_key = getKeyMapping(key)
                kv_pairs.append(f"{display_key}: {value}")
            record['changed_fields'] = "\n".join(kv_pairs)
    else:
        record['changed_fields'] = cf
    return record

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
    query = f"""SELECT a.auditlog_pk, a.object_id, b.name, a.action_date_time, a.origin, a.user, a.changed_fields
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
        tempData = process_changed_fields(item)
        if tempData['changed_fields'] is not None:
            data.append(tempData)
        
    
    now = datetime.now()
    currentDatetime = now.strftime("%Y-%m-%d_%H.%M.%S")
    fileName = "export/device42_auditlog_export_" + currentDatetime + ".xlsx"
    export_to_excel(data, fileName)

if __name__ == '__main__':
    main()