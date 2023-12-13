import subprocess

import frappe
from frappe import _
import json

def document_limit(doc, event):
    doctype_name = doc.doctype
    limit = frappe.get_site_config()['quota']
    doc_list = json.loads(limit) 
    
    for item in doc_list:
        if doctype_name in item:
            doc_count = item[doctype_name]
            count = frappe.db.count(doctype_name)
            if count > doc_count:
                frappe.throw(f"You have exceeded the maximum limit of {doctype_name}. Limit: {doc_count}, Current Count: {count}.")
            else:
                pass