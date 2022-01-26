# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _get_openapi_default_parameters(self):
        defaults = super(
            BaseShopinvaderService, self
        )._get_openapi_default_parameters()
        defaults.append(
            {
                "name": "PARTNER-EMAIL",
                "in": "header",
                "description": "Logged partner email "
                "(Only used when authenticated by auth_api_key)",
                "required": False,
                "schema": {"type": "string"},
                "style": "simple",
            }
        )
        defaults.append(
            {
                "name": "API-KEY",
                "in": "header",
                "description": "Ath API key "
                "(Only used when authenticated by auth_api_key)",
                "required": False,
                "schema": {"type": "string"},
                "style": "simple",
            }
        )
        return defaults

    def to_openapi(self):
        openapi = super(BaseShopinvaderService, self).to_openapi()
        api_key_scheme = {"type": "apiKey", "in": "header", "name": "API-KEY"}
        security_definitions = openapi.get("securityDefinitions", {})
        security_definitions["api_key"] = api_key_scheme
        openapi["securityDefinitions"] = security_definitions
        return openapi
