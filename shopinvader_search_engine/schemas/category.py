# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.category import (
    ShortShopinvaderCategory as BaseShortShopinvaderCategory,
)


class ShortShopinvaderCategory(BaseShortShopinvaderCategory, extends=True):
    @classmethod
    def from_shopinvader_category(cls, odoo_rec, with_hierarchy=False):
        obj = super().from_shopinvader_category(odoo_rec)
        if with_hierarchy:
            parent = odoo_rec.shopinvader_parent_id
            children = odoo_rec.shopinvader_child_ids
            obj.parent = (
                ShortShopinvaderCategory.from_shopinvader_category(parent)
                if parent
                else None
            )
            obj.childs = [
                ShortShopinvaderCategory.from_shopinvader_category(child)
                for child in children
            ]
        return obj
