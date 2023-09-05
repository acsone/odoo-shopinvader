# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)
from odoo.addons.shopinvader_product.schemas.product import ShopinvaderVariant


class ProductProductShopinvaderSerializer(PydanticModelSerializer):
    def __init__(self, index):
        self.index = index

    def get_model_class(self):
        return ShopinvaderVariant

    def serialize(self, record):
        return self.get_model_class().from_shopinvader_variant(record, index=self.index).model_dump()
