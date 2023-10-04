# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestBindingIndexBase


class TestCategoryBinding(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_records()

    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Category Index",
            "backend_id": backend.id,
            "model_id": cls.env["ir.model"]
            .search([("model", "=", "product.category")], limit=1)
            .id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "shopinvader_category_exports",
        }

    @classmethod
    def setup_records(cls, backend=None):
        backend = backend or cls.backend
        # create an index for category model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        # create a binding + category alltogether
        cls.category = cls.env["product.category"].create({"name": "Test category"})
        cls.category_binding = cls.category._add_to_index(cls.se_index)

    def test_serialize(self):
        self.category_binding.recompute_json()
        self.assertEqual(
            self.category_binding.data,
            {
                "id": self.category.id,
                "name": self.category.name,
                "sequence": None,
                "level": 0,
                "parent": None,
                "childs": [],
            },
        )

    def _create_parent_category(self):
        parent_category = self.env["product.category"].create(
            {"name": "Parent category"}
        )
        self.category.parent_id = parent_category
        return parent_category

    def test_serialize_hierarchy_parent_not_in_index(self):
        self._create_parent_category()
        self.category_binding.with_context(index=self.se_index).recompute_json()
        self.assertFalse(self.category_binding.data["parent"])

    def test_serialize_hierarchy_parent_in_index(self):
        parent_category = self._create_parent_category()
        self.category.invalidate_model()
        parent_category._add_to_index(self.se_index)
        self.category_binding.with_context(index=self.se_index).recompute_json()
        self.assertEqual(
            self.category_binding.data["parent"],
            {
                "id": parent_category.id,
                "name": "Parent category",
                "level": 0,
                "parent": None,
                "childs": [],
            },
        )
