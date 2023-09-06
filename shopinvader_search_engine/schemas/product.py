# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ShopinvaderVariant as BaseShopinvaderVariant,
)


class ShopinvaderVariant(BaseShopinvaderVariant, extends=True):
    @classmethod
    def from_shopinvader_variant(cls, odoo_rec, index=None, *args, **kwargs):
        obj = super().from_shopinvader_variant(odoo_rec, *args, **kwargs)
        obj.main = odoo_rec.with_context(index=index).main
        return obj
