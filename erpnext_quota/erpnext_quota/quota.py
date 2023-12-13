import frappe
import json

def document_limit(doc, event):
    try:
        doctype_name = doc.doctype
        limit_config = frappe.get_site_config().get('quota')

        if limit_config:
            doc_list = json.loads(limit_config)

            for item in doc_list:
                if doctype_name in item:
                    doc_count = item[doctype_name]
                    count = frappe.db.count(doctype_name)
                    if count > doc_count:
                        frappe.throw(f"You have exceeded the maximum limit of {doctype_name}. Limit: {doc_count}, Current Count: {count}.")
                    else:
                        pass

    except KeyError:
        pass
