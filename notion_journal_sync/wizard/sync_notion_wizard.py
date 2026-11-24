from odoo import models

class SyncNotionWizard(models.TransientModel):
    _name = 'sync.notion.wizard'
    _description = 'Wizard to Sync Notion Data'

    def sync_now(self):
        self.env['journal.sync.wizard'].create({}).sync_journal_entries()
