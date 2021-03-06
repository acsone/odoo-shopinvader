# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


class LocomotiveRole(models.Model):
    _name = 'locomotive.role'
    _description = 'Locomotive Customer Role'

    _rec_name = "code"

    backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')
    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        domain=[('type', '=', 'sale')])
    fiscal_position_ids = fields.Many2many(
        comodel_name='account.fiscal.position',
        relation='role_fiscal_position_rel',
        column1='role_id',
        column2='fiscal_position_id')
    code = fields.Char(required=True)
    default = fields.Boolean(
        string="Default role")

    _sql_constraints = [
        ('code_uniq', 'unique(backend_id, code)',
         'Code must be uniq per backend.'),
    ]

    @api.constrains('default', 'backend_id')
    def _check_default(self):
        if self.default:
            roles = self.search([
                ('default', '=', True),
                ('backend_id', '=', self.backend_id.id)])
            if len(roles) > 1:
                raise ValidationError(_("Only one default role is authorized"))

    @api.constrains('backend_id', 'pricelist_id', 'fiscal_position_ids')
    def _check_unique_pricelist_fposition(self):
        roles = self.search([
            ('backend_id', '=', self.backend_id.id),
            ('pricelist_id', '=', self.pricelist_id.id),
            ('fiscal_position_ids', 'in', self.fiscal_position_ids.ids)
            ])
        if len(roles) > 1:
            raise ValidationError(_(
                "Pricelist and fiscal position combination must be uniq "
                "per backend"))
