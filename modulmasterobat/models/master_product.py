from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ProductObat(models.Model):
    _name = 'master.product'
    _description = 'Master Produk Obat'
    _rec_name = 'nama'

    kode = fields.Char(string='Kode', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    nama = fields.Char(string='Nama Obat - AKSP', required=True)
    
    lkpp = fields.Selection([
        ('ya', 'Ya'),
        ('tidak', 'Tidak')
    ], string='LKPP')

    prb = fields.Selection([
        ('ya', 'Ya'),
        ('tidak', 'Tidak')
    ], string='PRB')

    prinsipal_id = fields.Many2one('master.prinsipal', string='Prinsipal')
    kontinuitas = fields.Selection([
        ('continue', 'Continue'),
        ('discontinue', 'Discontinue')
    ], string='Kontinuitas')

    satuan_id = fields.Many2one('master.satuan.barang', string='Satuan')
    harga_jual = fields.Float(string='Harga Jual')
    isi = fields.Float(string='Isi')
    harga_beli = fields.Float(string='Harga Beli')

    satuan_beli = fields.Float(string='Satuan Beli', compute='_compute_harga_satuan', store=True)
    satuan_jual = fields.Float(string='Satuan Jual', compute='_compute_harga_satuan', store=True)

    jenis_generik = fields.Selection([
        ('generik', 'Generik'),
        ('non_generik', 'Non Generik')
    ], string='Jenis Generik')

    klasifikasi_id = fields.Many2one('master.penanda.obat', string='Klasifikasi')

    status_validasi = fields.Selection([
        ('draft', 'Belum Disahkan'),
        ('disahkan', 'Sudah Disahkan')
    ], string='Status Validasi', default='draft')

    active = fields.Boolean(string='Active', default=True)

    komposisi_line_ids = fields.One2many(
        'master.product.komposisi.line',
        'product_id',
        string='Detail Komposisi'
    )

    persamaan_line_ids = fields.One2many(
        'master.product.persamaan.line',
        'product_id',
        string='Persamaan'
    )

    @api.model
    def create(self, vals):
        if vals.get('kode', _('New')) == _('New'):
            vals['kode'] = self.env['ir.sequence'].next_by_code('master.product') or _('New')
        return super(ProductObat, self).create(vals)

    def action_generate_persamaan(self):
        self.ensure_one()
        komposisi_ids = set(self.komposisi_line_ids.mapped('komposisi_id').ids)
        if not komposisi_ids:
            return
        self.persamaan_line_ids.unlink()
        domain = [('id', '!=', self.id)]
        other_products = self.search(domain)
        for other in other_products:
            other_komposisi_ids = set(other.komposisi_line_ids.mapped('komposisi_id').ids)
            if komposisi_ids == other_komposisi_ids:
                self.env['master.product.persamaan.line'].create({
                    'product_id': self.id,
                    'produk_persamaan_id': other.id,
                    'isi': other.isi,
                    'harga_beli': other.harga_beli,
                    'harga_jual': other.harga_jual,
                })

    @api.depends('harga_beli', 'harga_jual', 'isi')
    def _compute_harga_satuan(self):
        for rec in self:
            if rec.isi and rec.isi > 0:
                rec.satuan_beli = rec.harga_beli / rec.isi
                rec.satuan_jual = rec.harga_jual / rec.isi
            else:
                rec.satuan_beli = 0
                rec.satuan_jual = 0

    @api.onchange('harga_beli')
    def _onchange_harga_beli(self):
        """Otomatis isi harga_jual dengan PPN 11%"""
        for rec in self:
            if rec.harga_beli:
                rec.harga_jual = round(rec.harga_beli * 1.11)

    @api.onchange('isi')
    def _onchange_isi(self):
        """Otomatis isi satuan_jual dengan tambah 11%"""
        for rec in self:
            if rec.isi and rec.isi > 0:
                rec.satuan_jual = round(rec.isi * 1.11)
            else:
                rec.satuan_jual = 0

    def open_komposisi_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.komposisi.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_komposisi_ids': [(6, 0, self.komposisi_line_ids.mapped('komposisi_id').ids)],
                'form_view_initial_mode': 'readonly',
            },
            'flags': {
                'form': {
                    'action_buttons': False,
                    'options': {'mode': 'readonly'},
                    'hide_save_discard': True
                }
            }
        }
