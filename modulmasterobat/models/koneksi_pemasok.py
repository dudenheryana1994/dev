from odoo import models, fields, api

class KoneksiPemasok(models.Model):
    _name = 'koneksi.pemasok'
    _description = 'Koneksi Prinsipal ke Pemasok'

    prinsipal_id = fields.Many2one(
        'master.prinsipal', string='Nama Prinsipal', required=True, readonly=True, ondelete="cascade"
    )
    pemasok_id = fields.Many2one(
        'master.pemasok', string='Nama Pemasok', required=True, ondelete="restrict"
    )
    kode = fields.Char(string='Kode', readonly=True)
    alamat = fields.Text(string='Alamat', readonly=True)
    wiraniaga = fields.Char(string='Wiraniaga', readonly=True)
    no_hp = fields.Char(string='HP', readonly=True)

    @api.onchange('pemasok_id')
    def _onchange_pemasok_id(self):
        for rec in self:
            if rec.pemasok_id:
                rec.kode = rec.pemasok_id.kode
                rec.alamat = rec.pemasok_id.alamat
                rec.wiraniaga = rec.pemasok_id.kontak_person
                rec.no_hp = rec.pemasok_id.no_hp
            else:
                rec.kode = False
                rec.alamat = False
                rec.wiraniaga = False
                rec.no_hp = False

    def action_buat_pemasok(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Buat Pemasok Baru',
            'res_model': 'master.pemasok',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_prinsipal_id': self.prinsipal_id.id,
            }
        }
    
    @api.model
    def create(self, vals):
        if vals.get('pemasok_id'):
            pemasok = self.env['master.pemasok'].browse(vals['pemasok_id'])
            print('Pemasok:', pemasok.name, 'Kontak Person:', pemasok.kontak_person)
            vals.update({
                'kode': pemasok.kode,
                'alamat': pemasok.alamat,
                'wiraniaga': pemasok.kontak_person,
                'no_hp': pemasok.no_hp,
            })
        return super(KoneksiPemasok, self).create(vals)


