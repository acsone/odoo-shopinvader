# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import route

from odoo.addons.base_rest.controllers import main


class InvaderController(main.RestController):

    _root_path = "/shopinvader_jwt/"
    _collection_name = "shopinvader.backend"
    _default_auth = "jwt_shopinvader"
    _default_save_session = False
    _cors = "*"
    _component_context_provider = "shopinvader_auth_jwt_context_provider"

    @route(["/shopinvader/<service>/<int:_id>/download"], methods=["GET"])
    def service_download(self, service, _id=None, **params):
        params["id"] = _id
        return self._process_method(
            service, "download", _id=_id, params=params
        )
