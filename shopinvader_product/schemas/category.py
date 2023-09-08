# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from __future__ import annotations

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class ShortShopinvaderCategory(StrictExtendableBaseModel):
    id: int
    name: str
    level: int
    parent: ShortShopinvaderCategory | None = None
    childs: list[ShortShopinvaderCategory] = []

    @classmethod
    def from_shopinvader_category(cls, odoo_rec, with_hierarchy=False):
        obj = cls.model_construct(
            id=odoo_rec.id, name=odoo_rec.name, level=odoo_rec.short_description
        )
        if with_hierarchy:
            parent = odoo_rec.parent_id
            children = odoo_rec.child_id
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


class ShopinvaderCategory(ShortShopinvaderCategory):
    sequence: int | None = None

    @classmethod
    def from_shopinvader_category(cls, odoo_rec):
        obj = super().from_shopinvader_category(odoo_rec, with_hierarchy=True)
        obj.sequence = odoo_rec.sequence or None
        return obj
