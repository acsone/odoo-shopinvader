# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.category import (
    ShortShopinvaderCategory as BaseShortShopinvaderCategory,
)


class ShortShopinvaderCategory(BaseShortShopinvaderCategory, extends=True):
    @classmethod
    def from_shopinvader_category(
        cls, odoo_rec, with_hierarchy=False, index=None, *args, **kwargs
    ):
        obj = super().from_shopinvader_category(odoo_rec, *args, **kwargs)
        if with_hierarchy and index:
            parent = odoo_rec.parent_id.filtered(
                lambda parent, index=index: index
                in parent.se_binding_ids.mapped("index_id")
            )
            children = odoo_rec.child_id.filtered(
                lambda child, index=index: index
                in child.se_binding_ids.mapped("index_id")
            )
            obj.parent = (
                ShortShopinvaderCategory.from_shopinvader_category(
                    parent, *args, **kwargs
                )
                if parent
                else None
            )
            obj.childs = [
                ShortShopinvaderCategory.from_shopinvader_category(
                    child, *args, **kwargs
                )
                for child in children
            ]
        return obj
