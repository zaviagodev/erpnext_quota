import frappe
import json
from frappe.installer import update_site_config
import requests
from datetime import datetime, timedelta
from frappe.utils import get_site_name

def update_site_config_from_parent():
    last_run = frappe.get_site_config().get('last_run_time')
    if last_run:
        last_run_time = datetime.strptime(last_run, '%Y-%m-%d %H:%M:%S')
    else:
        last_run_time = datetime.min 

    current_time = datetime.now()

    # Check if 24 hours have passed
    if current_time - last_run_time >= timedelta(hours=24):
        update_config_file()
        frappe.get_site_config().update({
            'last_run_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        frappe.get_site_config().save()
    else:
        pass

def update_config_file():
    site_name = get_site_name(frappe.local.request.host)
    url = "https://hosting.zaviago.com/api/method/press.api.billing.get_quota?domain="+site_name
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        quota_data = data.get('message', [])
        update_site_config('quota', quota_data)
        return quota_data

def document_limit(doc, event):
    doctype_name = doc.doctype
    doc_list = frappe.get_site_config().get('quota')
    doc_list = json.loads(doc_list)
    if doc_list:
        for item in doc_list:
            if doctype_name in item:
                doc_count = item[doctype_name]
                count = frappe.db.count(doctype_name)
                if count > doc_count:
                    frappe.throw(f"You have exceeded the maximum limit of {doctype_name}. Limit: {doc_count}, Current Count: {count}.")
                    
            
@frappe.whitelist(allow_guest=True)
def get_list_of_usage():
    usage_counts = []
    doc_list = frappe.get_site_config().get('quota', [])
    doc_list = json.loads(doc_list)
    # Count documents for each doctype in doc_list
    for doctype_dict in doc_list:
        if isinstance(doctype_dict, dict):
            for doctype_name, quota_limit in doctype_dict.items():
                # Get the count of documents for the current doctype
                count = frappe.db.count(doctype_name)
                # Append the details to usage_counts
                usage_counts.append({
                    'doctype_name': doctype_name,
                    'quota_limit': quota_limit,
                    'quota_usage': count
                })

    # Count the number of admin users
    admin_user_count = frappe.db.count('User', filters={'user_type': 'System User'})
    
    # Count the number of installed apps
    installed_apps = frappe.get_installed_apps()
    installed_apps_count = len(installed_apps)
    
    return {
        'doctype_limit': usage_counts,
        'admin_user_count': admin_user_count,
        'installed_apps_count': installed_apps_count
    }
