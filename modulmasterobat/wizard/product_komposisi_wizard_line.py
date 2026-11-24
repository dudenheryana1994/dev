from odoo import models, fields

class ProductKomposisiWizardLine(models.TransientModel):
    _name = 'product.komposisi.wizard.line'
    _description = 'Line Komposisi untuk Wizard'

    wizard_id = fields.Many2one('product.komposisi.wizard', ondelete='cascade')
    komposisi_id = fields.Many2one('master.komposisi', string='Komposisi')
    kode = fields.Char(related='komposisi_id.kode', string='Kode', readonly=True)
