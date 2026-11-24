from odoo import models, fields

class ProductKomposisiLine(models.Model):
    _name = 'master.product.komposisi.line'
    _description = 'Detail Komposisi Obat'

    product_id = fields.Many2one('master.product', string='Produk Obat', ondelete='cascade')
    komposisi_id = fields.Many2one('master.komposisi', string='Komposisi', required=True)
    dosis = fields.Char(string='Dosis')
    satuan = fields.Char(string='Satuan')
    satukompo_id = fields.Many2one('master.satukompo', string='Satuan')
