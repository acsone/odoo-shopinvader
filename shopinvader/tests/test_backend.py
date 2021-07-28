# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class BackendCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(BackendCase, cls).setUpClass()
        cls.lang_fr = cls._install_lang("base.lang_fr")
        cls.env = cls.env(
            context=dict(cls.env.context, test_queue_job_no_delay=True)
        )
        cls.backend = cls.backend.with_context(test_queue_job_no_delay=True)

    def _bind_all_product(self):
        self.backend.bind_all_product()
        return (
            self.env["product.template"].search_count(
                [("sale_ok", "=", True)]
            ),
            self.env["shopinvader.product"].search_count([]),
        )

    def _bind_all_category(self):
        self.backend.bind_all_category()
        return (
            self.env["product.category"].search_count([]),
            self.env["shopinvader.category"].search_count([]),
        )

    def test_bind_all_product(self):
        self.assertEqual(*self._bind_all_product())

    def test_rebind_all_product(self):
        self._bind_all_product()
        self.env["shopinvader.variant"].search([], limit=1).unlink()
        self.assertEqual(*self._bind_all_product())

    def test_bind_all_category(self):
        self.assertEqual(*self._bind_all_category())

    def test_rebind_all_category(self):
        self._bind_all_category()
        self.env["shopinvader.category"].search([], limit=1).unlink()
        self._bind_all_category()
        self.assertEqual(
            self.env["product.category"].search_count([]),
            self.env["shopinvader.category"].search_count([]),
        )

    def test_add_new_lang_rebind(self):
        """
        Data:
            * A backend with 1 lang and all products binded for this lang
        Test Case:
            * Add a new lang
        Expected result:
            * A binding exits for each binded products in each lang
        """
        self._bind_all_product()
        self._bind_all_category()
        binded_variants_count = self.env["shopinvader.variant"].search_count(
            []
        )
        binded_categories_count = self.env[
            "shopinvader.category"
        ].search_count([])
        self.backend.write({"lang_ids": [(4, self.lang_fr.id)]})
        self.assertEqual(
            self.env["shopinvader.variant"].search_count([]),
            binded_variants_count * 2,
        )
        self.assertEqual(
            self.env["shopinvader.category"].search_count([]),
            binded_categories_count * 2,
        )

    def test_remove_lang_rebind(self):
        """
        Data:
            * A backend with 1 lang and all products binded for this lang
        Test Case:
            * Remove lang
        Expected result:
            * No binding exists
        """
        self._bind_all_product()
        self._bind_all_category()
        self.backend.write({"lang_ids": [(5, None, None)]})
        self.assertEqual(self.env["shopinvader.variant"].search_count([]), 0)
        self.assertEqual(self.env["shopinvader.category"].search_count([]), 0)

    def test_lookup_by_website_unique_key(self):
        website_unique_key = self.backend.website_unique_key
        self.assertTrue(website_unique_key)
        backend = self.env["shopinvader.backend"]._get_from_website_unique_key(
            website_unique_key
        )
        self.assertEqual(self.backend, backend)
        self.backend.website_unique_key = "new_key"
        backend = self.env["shopinvader.backend"]._get_from_website_unique_key(
            "new_key"
        )
        self.assertEqual(self.backend, backend)
