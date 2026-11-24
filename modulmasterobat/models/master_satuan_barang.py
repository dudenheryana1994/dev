from odoo import models, fields, api


class SatuanBarang(models.Model):
    _name = 'master.satuan.barang'
    _description = 'Master satuan barang'

    kode = fields.Char(string='Kode', readonly=True, copy=False)
    name = fields.Char(string='Nama Satuan', required=True)

    @api.model
    def create(self, vals):
        # Generate kode otomatis
        vals['kode'] = self.env['ir.sequence'].next_by_code(
            'master.satuan.barang') or 'New'
        return super(SatuanBarang, self).create(vals)