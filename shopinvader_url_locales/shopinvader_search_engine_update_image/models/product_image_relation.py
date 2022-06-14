# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class ProducImageRelation(models.Model):
    _inherit = "product.image.relation"

    @api.model
    def create(self, values):
        res = super(ProducImageRelation, self).create(values)
        res.product_tmpl_id.shopinvader_mark_to_update()
        return res

    def write(self, vals):
        res = super(ProducImageRelation, self).write(vals)
        self.mapped("product_tmpl_id").shopinvader_mark_to_update()
        return res

    def unlink(self):
        products = self.mapped("product_tmpl_id")
        res = super(ProducImageRelation, self).unlink()
        products.shopinvader_mark_to_update()
        return res
