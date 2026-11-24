from odoo import models, fields, api

class MasterKlasifikasi(models.Model):
    _name = 'master.klasifikasi'
    _description = 'Master Klasifikasi Pelanggan'
    _rec_name = 'kode'
    _rec_name = 'nama_klasifikasi'

    kode = fields.Char(string='Kode', required=True, copy=False,
                       readonly=True, default=lambda self: 'New')
    nama_klasifikasi = fields.Char(string='Klasifikasi', required=True)
    cara_bayar = fields.Selection(
        [('tunai', 'Tunai'), ('piutang', 'Piutang')],
        string='Cara Bayar',
        required=True
    )
    status = fields.Selection(
        [('hijau', 'Hijau'), ('merah', 'Merah')],
        string='Status',
        compute='_compute_status',
        store=True,
        default='hijau'
    )
    periode_aktif = fields.Date(string='Periode Aktif')

    @api.depends('cara_bayar')
    def _compute_status(self):
        for record in self:
            if record.cara_bayar == 'tunai':
                record.status = 'merah'
            elif record.cara_bayar == 'piutang':
                record.status = 'hijau'

    @api.model
    def create(self, vals):
        if vals.get('kode', 'New') == 'New':
            vals['kode'] = self.env['ir.sequence'].next_by_code(
                'master.klasifikasi.seq') or 'New'
        return super(MasterKlasifikasi, self).create(vals)
    
    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.kode} {rec.nama_klasifikasi}"
            result.append((rec.id, name))
        return result


