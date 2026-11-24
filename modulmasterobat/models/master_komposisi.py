from odoo import models, fields, api


class Komposisi(models.Model):
    _name = 'master.komposisi'
    _description = 'Master Komposisi'

    kode = fields.Char(string='Kode', readonly=True, copy=False)
    name = fields.Char(string='Nama Generik', required=True)

    @api.model
    def create(self, vals):
        # Generate kode otomatis
        vals['kode'] = self.env['ir.sequence'].next_by_code(
            'master.komposisi') or 'New'
        return super(Komposisi, self).create(vals)