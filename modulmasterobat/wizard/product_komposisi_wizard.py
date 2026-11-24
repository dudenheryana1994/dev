from odoo import models, fields, api

class ProductKomposisiWizard(models.TransientModel):
    _name = 'product.komposisi.wizard'
    _description = 'Wizard Pencarian Persamaan Produk Berdasarkan Komposisi'

    komposisi_ids = fields.Many2many('master.komposisi', string='Komposisi yang Dicari')

    hasil_ids = fields.One2many(
        'product.komposisi.wizard.hasil',
        'wizard_id',
        string='Hasil Pencarian'
    )

    def cari_salah_satu(self):
        komposisi_ids = self.komposisi_ids.ids
        domain = [('komposisi_line_ids.komposisi_id', 'in', komposisi_ids)]
        produk_ids = self.env['master.product'].search(domain)
        self._update_hasil(produk_ids)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.komposisi.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'readonly',
            },
            'flags': {
                'form': {
                    'action_buttons': False,
                    'options': {'mode': 'readonly', 'hide_save_discard': True}
                }
            }
        }

    def cari_komposisi_sama(self):
        komposisi_ids = set(self.komposisi_ids.ids)
        produk_ids = []
        for produk in self.env['master.product'].search([]):
            prod_kompo = set(produk.komposisi_line_ids.mapped('komposisi_id').ids)
            if prod_kompo == komposisi_ids:
                produk_ids.append(produk.id)
        self._update_hasil(self.env['master.product'].browse(produk_ids))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.komposisi.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'readonly',
            },
            'flags': {
                'form': {
                    'action_buttons': False,
                    'options': {'mode': 'readonly', 'hide_save_discard': True}
                }
            }
        }

    def _update_hasil(self, produk_records):
        self.hasil_ids.unlink()
        for prod in produk_records:
            self.env['product.komposisi.wizard.hasil'].create({
                'wizard_id': self.id,
                'product_id': prod.id,
                'prinsipal': prod.prinsipal_id.nama_prinsipal or '',
                'generik': prod.jenis_generik or '',
                'jenis': prod.klasifikasi_id.name or '',
                'harga_beli': prod.harga_beli or 0.0,
            })

