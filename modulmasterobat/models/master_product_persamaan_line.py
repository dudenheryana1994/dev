from odoo import models, fields

class ProductPersamaanLine(models.Model):
    _name = 'master.product.persamaan.line'
    _description = 'Persamaan Barang'

    product_id = fields.Many2one('master.product', string='Produk Obat', ondelete='cascade')
    produk_persamaan_id = fields.Many2one('master.product', string='Produk Persamaan', readonly=True)
    isi = fields.Float(string='Isi', readonly=True)
    harga_beli = fields.Float(string='Harga Beli', readonly=True)
    harga_jual = fields.Float(string='Harga Jual', readonly=True)
