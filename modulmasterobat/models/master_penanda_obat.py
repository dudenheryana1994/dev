from odoo import models, fields, api


class PenandaObat(models.Model):
    _name = 'master.penanda.obat'
    _description = 'Master Penanda Obat'

    kode = fields.Char(string='Kode', readonly=True, copy=False)
    name = fields.Char(string='Nama Penanda', required=True)
    status = fields.Selection([
        ('hijau', 'Hijau'),
        ('biru', 'Biru'),
        ('merah', 'Merah'),
    ], string='Status', default='hijau')

    @api.model
    def create(self, vals):
        # Generate kode otomatis
        vals['kode'] = self.env['ir.sequence'].next_by_code(
            'master.penanda.obat') or 'New'
        return super(PenandaObat, self).create(vals)