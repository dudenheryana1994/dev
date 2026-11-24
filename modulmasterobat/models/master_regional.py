from odoo import models, fields, api

class MasterRegional(models.Model):
    _name = 'master.regional'
    _description = 'Master Regional'
    _rec_name = 'kode_regional'
    _rec_name = 'name'

    kode_regional = fields.Char(string='Kode Regional', required=True, readonly=True, default='New')
    name = fields.Char(string='Nama Regional', required=True)

    pemasok_id = fields.Many2one('master.pemasok', string='Nama Gudang', required=True)
    kode_gudang = fields.Char(string='Kode Gudang', compute='_compute_kode_gudang', store=True)

    @api.model
    def create(self, vals):
        if vals.get('kode_regional', 'New') == 'New':
            vals['kode_regional'] = self.env['ir.sequence'].next_by_code('master.regional') or 'New'
        return super().create(vals)

    @api.depends('pemasok_id')
    def _compute_kode_gudang(self):
        for rec in self:
            rec.kode_gudang = rec.pemasok_id.kode if rec.pemasok_id else ''

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.name} - {rec.name}"
            result.append((rec.id, name))
        return result

