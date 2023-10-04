# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class ProductCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.variant = cls.env.ref("product.product_product_4b")

    def test_product_shopinvader_categories(self):
        product = self.env.ref("product.product_product_4")
        self.assertEqual(len(product.shopinvader_categ_ids), 3)

    def test_variant_attributes(self):
        attr_dict = {"legs": "Steel", "color": "Black"}
        self.assertDictEqual(self.variant.variant_attributes, attr_dict)

    def test_main_product(self):
        variants = self.template.product_variant_ids
        main_variant = variants.filtered(lambda v: v.main)
        self.assertEqual(len(main_variant), 1)
        self.assertNotIn(
            True,
            variants.filtered(lambda x: x.id != main_variant.id).mapped("main"),
        )
        # change order
        main_variant.default_code = "ZZZZZZZ"
        main_variant.name = "ZZZZZZ"
        variants.invalidate_recordset()
        main_variant1 = variants.filtered(lambda v: v.main)
        self.assertNotEqual(main_variant, main_variant1)
        self.assertEqual(len(main_variant1), 1)
        self.assertNotIn(
            True,
            variants.filtered(lambda x: x.id != main_variant1.id).mapped("main"),
        )
