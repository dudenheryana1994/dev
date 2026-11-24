from odoo import models, fields

class ProductKomposisiWizardHasil(models.TransientModel):
    _name = 'product.komposisi.wizard.hasil'
    _description = 'Hasil Pencarian Komposisi Produk'

    wizard_id = fields.Many2one('product.komposisi.wizard', ondelete='cascade')
    product_id = fields.Many2one('master.product', string='Nama Obat')
    prinsipal = fields.Char(string='Prinsipal')
    generik = fields.Char(string='Generik')
    jenis = fields.Char(string='Jenis')
    harga_beli = fields.Float(string='Harga Beli')
