from odoo import models, fields, api


class MasterPrinsipal(models.Model):
    _name = 'master.prinsipal'
    _description = 'Master Prinsipal'
    _rec_name = 'nama_prinsipal'

    kode = fields.Char(string='Kode', required=True)
    nama_prinsipal = fields.Char(string='Nama Prinsipal', required=True)
    sales = fields.Char(string='Sales')
    kontak_person = fields.Char(string='Kontak Person')
    telp = fields.Char(string='Telepon')
    email = fields.Char(string='Email')
    alamat = fields.Char(string='Alamat')
    alamat2 = fields.Char(string='Alamat 2')
    alamat_full = fields.Char(string='Alamat Lengkap',
                              compute='_compute_alamat_full')
    koneksi_pemasok_count = fields.Integer(
        string='Jumlah Koneksi Pemasok', compute='_compute_koneksi_pemasok_count')

    koneksi_pemasok_ids = fields.One2many(
        'koneksi.pemasok', 'prinsipal_id', string='Koneksi Pemasok'
    )
    
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.nama_prinsipal))
        return result

    @api.depends('alamat', 'alamat2')
    def _compute_alamat_full(self):
        for record in self:
            record.alamat_full = f"{record.alamat} {record.alamat2}" if record.alamat2 else record.alamat

    @api.depends('koneksi_pemasok_ids')
    def _compute_koneksi_pemasok_count(self):
        for record in self:
            record.koneksi_pemasok_count = len(record.koneksi_pemasok_ids)

    def action_koneksi_pemasok(self):
        """Buka popup daftar koneksi pemasok berdasarkan prinsipal yang dipilih"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Koneksi Pemasok',
            'res_model': 'koneksi.pemasok',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('modulmasterobat.view_koneksi_pemasok_tree').id, 'tree'),
                (self.env.ref('modulmasterobat.view_koneksi_pemasok_form').id, 'form')
            ],
            'target': 'new',
            'domain': [('prinsipal_id', '=', self.id)],
            'context': {'default_prinsipal_id': self.id},
        }