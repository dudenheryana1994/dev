# -*- coding: utf-8 -*-
import requests
import pytz
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

# ==== Notion API Config ====
NOTION_API_KEY = ''
DATABASE_ID = ''
NOTION_VERSION = '2022-06-28'

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}


class AccountMoveTimestamps(models.Model):
    _inherit = 'account.move'

    start_time = fields.Datetime(string="Start Time", readonly=True, default=fields.Datetime.now)
    end_time = fields.Datetime(string="End Time", readonly=True)
    duration_minutes = fields.Integer(string="Duration (minutes)", compute="_compute_duration", store=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                diff = rec.end_time - rec.start_time
                rec.duration_minutes = int(diff.total_seconds() / 60)
            else:
                rec.duration_minutes = 0

    @api.model
    def create(self, vals):
        if not vals.get('start_time'):
            vals['start_time'] = fields.Datetime.now()
        return super().create(vals)

    def action_post(self):
        res = super().action_post()
        for rec in self:
            if not rec.end_time:
                rec.end_time = fields.Datetime.now()
            rec._push_to_notion()
        return res

    def _to_iso_with_tz(self, dt):
        if not dt:
            return None
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        return dt.astimezone(user_tz).isoformat()

    def _push_to_notion(self):
        url = "https://api.notion.com/v1/pages"
        for rec in self:
            # Pastikan durasi dihitung ulang
            rec._compute_duration()

            start_iso = self._to_iso_with_tz(rec.start_time)
            end_iso = self._to_iso_with_tz(rec.end_time)

            if not start_iso or not end_iso:
                _logger.warning(f"Skipping Notion push for {rec.name} because start/end time is missing.")
                continue

            payload = {
                "parent": {"database_id": DATABASE_ID},
                "properties": {
                    "User": {
                        "title": [
                            {"text": {"content": str(rec.create_uid.name or rec.env.user.name)}}
                        ]
                    },
                    "Start Time": {"date": {"start": start_iso}},
                    "End Time": {"date": {"start": end_iso}},
                    "Duration": {"number": rec.duration_minutes}
                }
            }

            try:
                resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
                if resp.status_code >= 400:
                    _logger.error(
                        "Notion push failed: status=%s, body=%s, payload=%s",
                        resp.status_code, resp.text, payload
                    )
            except Exception as e:
                _logger.exception("Exception while pushing to Notion: %s", e)
