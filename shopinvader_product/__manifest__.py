# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product",
    "summary": """Adds shopinvader product fields and schemas""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "base_sparse_field",
        "product",
        "pydantic",
        "extendable",
        "extendable_fastapi",
        "shopinvader_base_url",
    ],
    "data": [],
    "demo": [],
    "external_dependencies": {
        "python": ["extendable_pydantic>=1.1.1", "pydantic>=2.0.0"]
    },
    "installable": True,
}
