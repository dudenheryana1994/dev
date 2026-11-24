# -*- coding: utf-8 -*-
import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

NOTION_API_KEY = ''
DATABASE_ID = '2462b3866ce280399a13d16be801ea83'
NOTION_VERSION = '2022-06-28'

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

class JournalSync(models.TransientModel):
    _name = 'journal.sync.wizard'
    _description = 'Sync Journal Entries from Notion'

    def fetch_notion_data(self):
        """Ambil data dari Notion"""
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, headers=HEADERS)

        if response.status_code != 200:
            _logger.error("Failed to fetch data from Notion: %s", response.text)
            return []

        return response.json().get('results', [])

    def parse_notion_entry(self, page):
        """Parsing satu halaman Notion ke format entry dict"""
        try:
            props = page.get('properties', {})

            reference = ''
            if props.get('Reference', {}).get('title'):
                reference = props['Reference']['title'][0]['text']['content']

            account_name = ''
            if props.get('Account', {}).get('rich_text'):
                account_name = props['Account']['rich_text'][0].get('plain_text', '').strip()

            debit = props.get('Debit', {}).get('number') or 0.0
            credit = props.get('Credit', {}).get('number') or 0.0
            date = props.get('Accounting Date', {}).get('date', {}).get('start')

            return {
                'reference': reference,
                'account_name': account_name,
                'debit': debit,
                'credit': credit,
                'date': date
            }
        except Exception as e:
            _logger.error(f"Error parsing entry: {e}")
            return None

    def sync_journal_entries(self):
        """Sinkronisasi data dari Notion ke Odoo"""
        notion_data = self.fetch_notion_data()

        for page in notion_data:
            entry = self.parse_notion_entry(page)
            if not entry:
                continue

            # Cek apakah entry sudah ada di Odoo berdasarkan reference
            existing_move = self.env['account.move'].search([
                ('ref', '=', entry['reference'])
            ], limit=1)

            if existing_move:
                _logger.info("Skipping existing journal entry with ref: %s", entry['reference'])
                continue

            # Ekstrak kode akun (misal: "1.1.01.005 Kas Bank" -> "1.1.01.005")
            account_code = entry['account_name'].split()[0]
            account = self.env['account.account'].search([
                ('code', '=', account_code)
            ], limit=1)

            if not account:
                _logger.warning("Account not found: %s", account_code)
                continue

            # Cari jurnal umum (general)
            journal = self.env['account.journal'].search([
                ('type', '=', 'general')
            ], limit=1)

            if not journal:
                _logger.error("No general journal found.")
                continue

            # Siapkan line untuk debit dan credit
            line_ids = []

            if entry['debit'] > 0:
                line_ids.append((0, 0, {
                    'account_id': account.id,
                    'debit': entry['debit'],
                    'credit': 0.0,
                    'name': entry['reference'],
                }))

            if entry['credit'] > 0:
                line_ids.append((0, 0, {
                    'account_id': account.id,
                    'debit': 0.0,
                    'credit': entry['credit'],
                    'name': entry['reference'],
                }))

            if not line_ids:
                _logger.warning("Skipping entry with zero debit and credit: %s", entry['reference'])
                continue

            # Buat jurnal entry
            move_vals = {
                'ref': entry['reference'],
                'date': entry['date'],
                'journal_id': journal.id,
                'line_ids': line_ids
            }

            move = self.env['account.move'].create(move_vals)
            _logger.info("Journal Entry Created: %s", move.name)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
