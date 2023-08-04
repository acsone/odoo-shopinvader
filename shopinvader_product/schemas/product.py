# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Any

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel

from .category import ShortShopinvaderCategory


class ShopinvaderProduct(StrictExtendableBaseModel):
    name: str

    @classmethod
    def from_shopinvader_product(cls, odoo_rec):
        return cls.model_construct(name=odoo_rec.shopinvader_display_name)


class ShopinvaderProductPriceInfo(StrictExtendableBaseModel):
    value: float = 0
    tax_included: bool = False
    original_value: float = 0
    discount: float = 0


class ShopinvaderVariant(StrictExtendableBaseModel):
    id: int
    model: ShopinvaderProduct
    main: bool = False
    short_description: str | None = None
    description: str | None = None
    full_name: str | None = None
    short_name: str | None = None
    seo_title: str | None = None
    meta_keywords: str | None = None
    variant_count: int | None = None
    categories: list[ShortShopinvaderCategory] = []
    sku: str | None = None
    variant_attributes: dict[str, Any] = {}
    price: dict[str, ShopinvaderProductPriceInfo] = {}

    @classmethod
    def from_shopinvader_variant(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            model=ShopinvaderProduct.from_shopinvader_product(odoo_rec.product_tmpl_id),
            main=odoo_rec.main,
            short_description=odoo_rec.short_description or None,
            description=odoo_rec.description or None,
            full_name=odoo_rec.name or None,
            short_name=odoo_rec.short_name or None,
            seo_title=odoo_rec.seo_title or None,
            meta_keywords=odoo_rec.meta_keywords or None,
            variant_count=odoo_rec.variant_count or None,
            categories=[
                ShortShopinvaderCategory.from_shopinvader_category(shopinvader_category)
                for shopinvader_category in odoo_rec.shopinvader_categ_ids
            ],
            sku=odoo_rec.default_code or None,
            variant_attributes=odoo_rec.variant_attributes,
            price=odoo_rec.price,
        )