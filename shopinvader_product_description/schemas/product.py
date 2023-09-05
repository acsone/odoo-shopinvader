# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ShopinvaderVariant as BaseShopinvaderVariant,
)


class ShopinvaderVariant(BaseShopinvaderVariant, extends=True):
    short_description: str | None = None
    description: str | None = None

    @classmethod
    def from_shopinvader_variant(cls, odoo_rec, *args, **kwargs):
        obj = super().from_shopinvader_variant(odoo_rec, *args, **kwargs)
        obj.short_description = odoo_rec.description_sale_short or None
        obj.description = odoo_rec.description_sale_long or None
        return obj
