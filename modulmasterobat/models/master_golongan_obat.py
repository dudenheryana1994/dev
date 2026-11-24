from odoo import models, fields, api


class GolonganObat(models.Model):
    _name = 'master.golongan.obat'
    _description = 'Master Golongan Obat'

    kode = fields.Char(string='Kode', readonly=True, copy=False)
    name = fields.Char(string='Nama Golongan', required=True)
    status = fields.Selection([
        ('hijau', 'Hijau'),
        ('biru', 'Biru'),
        ('merah', 'merah'),
    ], string='Status', default='hijau')

    @api.model
    def create(self, vals):
        # Generate kode otomatis
        vals['kode'] = self.env['ir.sequence'].next_by_code(
            'master.golongan.obat') or 'New'
        return super(GolonganObat, self).create(vals)