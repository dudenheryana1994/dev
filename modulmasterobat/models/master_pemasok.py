import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MasterPemasok(models.Model):
    _name = 'master.pemasok'
    _description = 'Master Pemasok'
    _rec_name = 'nama_pemasok'

    name = fields.Char(related='nama_pemasok', string='Nama Pemasok', store=True)

    prinsipal_id = fields.Many2one('master.prinsipal', string='Prinsipal')

    kode = fields.Char(string='Kode', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    bpom = fields.Char(string='Kode BPOM', required=True)
    nama_pemasok = fields.Char(string='Nama Pemasok', required=True)
    alamat = fields.Text(string='Alamat')
    alamat2 = fields.Char(string='Alamat 2')
    alamat_full = fields.Char(string='Alamat Lengkap',
                              compute='_compute_alamat_full', store=True)

    # Gunakan Many2one untuk memilih data dari master.regional
    #regional_id = fields.Many2one('master.regional', string='Regional')

    # Jadikan kode_pos dan nama_regional sebagai related field
    #kode_pos = fields.Char(string='Kode Pos', related='regional_id.kode_regional', store=True, readonly=False)
    #nama_regional = fields.Char(string='Nama Regional', related='regional_id.regional', store=True, readonly=False)

    # Tambahkan relasi ke master.regional
    kode_pos_id = fields.Many2one('master.regional', string='Kode Pos')
    nama_regional = fields.Char(string='Nama Regional', related='kode_pos_id.name', store=True, readonly=True)

    izin_pemasok = fields.Char(string='Izin Pemasok', required=True)
    periode_aktif = fields.Date(string='Berlaku s.d')

    cara_bayar = fields.Selection([
        ('cash', 'Cash'),
        ('kredit', 'Kredit')
    ], string="Cara Bayar", default="cash", required=True)

    apoteker_pj = fields.Char(string='Apoteker PJ', required=True)
    nomor_sipa = fields.Char(string='Nomor SIPA', required=True)
    tgl_berlaku = fields.Date(string='Tgl Berlaku', required=True)
    no_hp = fields.Char(string='HP', required=True)
    
    status = fields.Selection([
        ('pkp', 'P.K.P'),
        ('non_pkp', 'Non P.K.P')
    ], string="Status", default="pkp", required=True)

    npwp = fields.Char(string='N.P.W.P')
    nitku = fields.Char(string='N.I.T.K.U')

    posisi_ppn = fields.Selection([
        ('gabung', 'Gabung'),
        ('dipisah', 'Dipisah',)
    ], string="Posisi PPN", default="dipisah", required=True)

    min_order = fields.Integer(string='Min. Order', default=0)

    jenis_pemasok = fields.Selection([
        ('industri', 'Industri'),
        ('pbf', 'PBF')
    ], string="Jenis Pemasok", required=True, default='pbf')

    diseleksi_oleh = fields.Selection([
        ('apoteker', 'Apoteker'),
        ('pembelian', 'Pembelian')
    ], string="Diseleksi Oleh", required=True, default='apoteker')

    daftar_harga = fields.Selection([
        ('setuju', 'Setuju'),
        ('tidak', 'Tidak')
    ], string="Daftar Harga", required=True, default='setuju')

    tdp_nib = fields.Selection([
        ('aktif', 'Aktif'),
        ('tidak', 'Tidak')
    ], string="TDP/NIB", required=True, default='aktif')

    copob_cdob = fields.Selection([
        ('berlaku', 'Berlaku'),
        ('expired', 'Expired')
    ], string="Sertifikasi COPOB/CDOB", required=True, default='berlaku')

    siup = fields.Selection([
        ('berlaku', 'Berlaku'),
        ('expired', 'Expired')
    ], string="SIUP", required=True, default='berlaku')

    kesimpulan = fields.Selection([
        ('terima', 'Terima'),
        ('tolak', 'Tolak')
    ], string="Kesimpulan", required=True, default='terima')

    wiraniaga = fields.Char(string='Wiraniaga')
    kontak_person = fields.Char(string='Kontak Person', required=True)
    telp = fields.Char(string='Telepon', required=True)
    email = fields.Char(string='Email')
    tempo = fields.Integer(string='Tempo [Hari]', default=0)
    no_rekening = fields.Char(string='Nomor Rekening')
    nama_bank = fields.Char(string='Nama Bank')
    atas_nama = fields.Char(string='Atas Nama')

    @api.model
    def create(self, vals):
        if vals.get('kode', 'New') == 'New':
            vals['kode'] = self.env['ir.sequence'].next_by_code(
                'master.pemasok') or 'New'
        return super(MasterPemasok, self).create(vals)

    # Compute full address
    @api.depends('alamat', 'alamat2')
    def _compute_alamat_full(self):
        for rec in self:
            rec.alamat_full = f"{rec.alamat or ''} {rec.alamat2 or ''}".strip()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled')
    ], default='draft')

    def approve(self):
        self.state = 'approved'

    def cancel(self):
        self.state = 'canceled'

    @api.constrains('npwp')
    def _check_npwp(self):
        for rec in self:
            if rec.npwp and not re.fullmatch(r'\d{16}', rec.npwp):
                raise ValidationError(_('NPWP harus terdiri dari 16 digit angka'))
    
    @api.constrains('nitku')
    def _check_nitku(self):
        for rec in self:
            if rec.nitku and not re.fullmatch(r'\d{23}', rec.nitku):
                raise ValidationError(_('NITKU harus terdiri dari 23 digit angka'))

