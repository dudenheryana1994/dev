from odoo import models, fields, api


class SatuanKomposisi(models.Model):
    _name = 'master.satukompo'
    _description = 'Master Satuan Komposisi'

    kode = fields.Char(string='Kode', readonly=True, copy=False)
    name = fields.Char(string='Nama Satuan', required=True)

    @api.model
    def create(self, vals):
        # Generate kode otomatis
        vals['kode'] = self.env['ir.sequence'].next_by_code(
            'master.satukompo') or 'New'
        return super(SatuanKomposisi, self).create(vals)