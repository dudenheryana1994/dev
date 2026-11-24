import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # klasifikasi_pelanggan = fields.Char(string="Nama Klasifikasi Pelanggan")
    klasifikasi_pelanggan = fields.Many2one(
    'master.klasifikasi',
    string="Klasifikasi Pelanggan Pelanggan",
    )
    # wilayah = fields.Char(string="Wilayah")
    wilayah = fields.Many2one(
    'master.regional',
    string='Wilayah'
    )
    pemilik = fields.Char(string="Pemilik")
    no_ijin = fields.Char(string="No Izin Sarana")
    masa_berlaku = fields.Date(string="Masa Berlaku")
    penanggung_jawab = fields.Char(string="Penanggung Jawab (Apt)")
    no_ijin_apt = fields.Char(string="No Izin")
    masa_berlaku_apt = fields.Date(string="Masa Berlaku")

    jenis_jual = fields.Selection([
        ('gudang', 'Gudang'),
        ('depo', 'Depo'),
        ('konsinyasi', 'Konsinyasi')
    ], string="Jenis Jual")

    kunci_jual = fields.Selection([
        ('ya', 'Ya'),
        ('tidak', 'Tidak')
    ], string="Kunci Jual")

    jenis_izin = fields.Selection([
        ('apotek', 'Apotek'),
        ('puskesmas', 'Puskesmas'),
        ('rs', 'Instalasi Farmasi RS'),
        ('klinik', 'Instalasi Farmasi Klinik'),
        ('dokter', 'Dokter Praktik'),
        ('pasien', 'Pasien'),
        ('toko', 'Toko Obat'),
        ('gudang', 'Gudang')
    ], string="Jenis Izin")

    fax = fields.Char(string="Fax")

    @api.constrains('vat')
    def _check_npwp(self):
        for rec in self:
            if rec.vat and not re.fullmatch(r'\d{16}', rec.vat):
                raise ValidationError(_('NPWP harus terdiri dari 16 digit angka'))
            
    nama_wp = fields.Char(string="Nama Wajib Pajak")
