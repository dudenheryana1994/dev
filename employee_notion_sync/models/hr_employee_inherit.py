import logging
import requests
import json
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
_logger.warning(">>> FILE hr_employee_inherit.py DILOAD <<<")

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    team = fields.Char(string="Team")
    nik_ktp = fields.Char(string="NIK KTP")
    telegram_id = fields.Char(string="ID Telegram")
    telegram_username = fields.Char(string="Username Telegram")
    card = fields.Char(string="Card")
    status = fields.Selection([
        ('active', 'Active'),
        ('non_active', 'Non Active')
    ], string='Status', default='active')
    salary_per_month = fields.Float(string='Salary / Month')    

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        _logger.warning(">>>> MASUK KE METHOD CREATE (%s records)", len(records))
        for record in records:
            _logger.info("CREATE: Employee created with ID %s and name '%s'", record.id, record.name)
            try:
                record.send_to_notion()
            except Exception:
                _logger.exception("send_to_notion failed on create for '%s'", record.name)
        return records

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            _logger.info("WRITE: Employee updated with ID %s and name '%s'", record.id, record.name)
            record.send_to_notion()
        return res

    def send_to_notion(self):
        notion_token = ""
        database_id = ""
        notion_url = "https://api.notion.com/v1/pages"
        notion_query_url = f"https://api.notion.com/v1/databases/{database_id}/query"

        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        def safe_str(value):
            if hasattr(value, 'name'):
                return value.name
            return str(value) if value else ""

        for employee in self:
            try:
                work_phone = safe_str(employee.work_phone)
                if not work_phone:
                    _logger.warning("Employee '%s' has no Work Phone. Skipping Notion sync.", employee.name)
                    continue

                # Step 1: Query Notion by Work Phone
                query_payload = {
                    "filter": {
                        "property": "Work Phone",
                        "rich_text": {
                            "equals": work_phone
                        }
                    }
                }

                query_resp = requests.post(notion_query_url, headers=headers, json=query_payload)
                if query_resp.status_code != 200:
                    _logger.error("Failed to query Notion for employee '%s': %s", employee.name, query_resp.text)
                    continue

                query_data = query_resp.json()
                existing_pages = query_data.get("results", [])

                properties = {
                    "Employee Name": {
                        "title": [{"text": {"content": safe_str(employee.name)}}]
                    },
                    "Tags": {
                        "rich_text": [{"text": {"content": safe_str(tag.name)}} for tag in employee.category_ids] if employee.category_ids else []
                    },
                    "Job Title": {
                        "rich_text": [{"text": {"content": safe_str(employee.job_title)}}]
                    },
                    "Job Position": {
                        "rich_text": [{"text": {"content": safe_str(employee.job_id.name if employee.job_id else "")}}]
                    },
                    "Work Mobile": {
                        "rich_text": [{"text": {"content": safe_str(employee.mobile_phone)}}]
                    },
                    "Work Phone": {
                        "rich_text": [{"text": {"content": work_phone}}]
                    },
                    "Work Email": {
                        "email": safe_str(employee.work_email)
                    },
                    "Company": {
                        "rich_text": [{"text": {"content": safe_str(employee.company_id.name)}}]
                    },
                    "Department": {
                        "rich_text": [{"text": {"content": safe_str(employee.department_id.name)}}]
                    },
                    "Manager": {
                        "rich_text": [{"text": {"content": safe_str(employee.parent_id.name if employee.parent_id else "")}}]
                    },
                    "Coach": {
                        "rich_text": [{"text": {"content": safe_str(employee.coach_id.name if employee.coach_id else "")}}]
                    },
                    "Work Address": {
                        "rich_text": [{"text": {"content": safe_str(employee.address_id.display_name if employee.address_id else "")}}]
                    },
                    "Work Location": {
                        "rich_text": [{"text": {"content": safe_str(employee.work_location_id.name if employee.work_location_id else "")}}]
                    },
                    "Working Hours": {
                        "rich_text": [{"text": {"content": safe_str(employee.resource_calendar_id.name if employee.resource_calendar_id else "")}}]
                    },
                    "Timezone": {
                        "rich_text": [{"text": {"content": safe_str(employee.tz)}}]
                    },
                    "Employee Type": {
                        "rich_text": [{"text": {"content": safe_str(employee.employee_type)}}]
                    },
                    "Related User": {
                        "rich_text": [{"text": {"content": safe_str(employee.user_id.name if employee.user_id else "")}}]
                    },
                    "PIN Code": {
                        "rich_text": [{"text": {"content": safe_str(employee.pin if employee.pin else "")}}]
                    },
                    "Team": {
                        "rich_text": [{"text": {"content": safe_str(employee.team)}}]
                    },
                    "NIK KTP": {
                        "rich_text": [{"text": {"content": safe_str(employee.nik_ktp)}}]
                    },
                    "ID Telegram": {
                        "rich_text": [{"text": {"content": safe_str(employee.telegram_id)}}]
                    },
                    "Username Telegram": {
                        "rich_text": [{"text": {"content": safe_str(employee.telegram_username)}}]
                        },
                    "Status": {
                        "select": {"name": safe_str(employee.status)}
                    },
                    "Salary / Month": {
                        "number": employee.salary_per_month or 0
                    }
                }

                if existing_pages:
                    # Step 2: Update
                    page_id = existing_pages[0]["id"]
                    update_url = f"https://api.notion.com/v1/pages/{page_id}"
                    update_resp = requests.patch(update_url, headers=headers, json={"properties": properties})

                    if update_resp.status_code == 200:
                        _logger.info("Updated existing Notion page for '%s'", employee.name)
                    else:
                        _logger.error("Failed to update Notion for '%s': %s", employee.name, update_resp.text)
                else:
                    # Step 3: Create
                    create_payload = {
                        "parent": {"database_id": database_id},
                        "properties": properties
                    }

                    create_resp = requests.post(notion_url, headers=headers, json=create_payload)

                    if create_resp.status_code in (200, 201):
                        _logger.info("Created new Notion page for '%s'", employee.name)
                    else:
                        _logger.error("Failed to create Notion page for '%s' [Status: %s]: %s", employee.name, create_resp.status_code, create_resp.text)

            except Exception as e:
                _logger.exception("Error syncing employee '%s' to Notion: %s", employee.name, str(e))
