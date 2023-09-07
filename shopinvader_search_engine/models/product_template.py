# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _filter_categories_by_index(self, categories):
        index = self._context.get("index", False)
        if index:
            categories = categories.filtered(
                lambda category, index=index: index
                in category.se_binding_ids.mapped("index_id")
            )
        return categories

    def _get_categories(self):
        self.ensure_one()
        categories = super()._get_categories()
        self._filter_categories_by_index(categories)
        return categories

    @api.model
    def _get_parent_categories(self, categ_ids):
        categories = super()._get_parent_categories(categ_ids)
        self._filter_categories_by_index(categories)
        return categories

    @api.depends_context("index")
    @api.depends("categ_id", "categ_id.parent_id")
    def _compute_shopinvader_category(self):
        return super()._compute_shopinvader_category()
