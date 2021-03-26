# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super
from contextlib import contextmanager

import mock

from odoo.exceptions import MissingError
from odoo.tests import SavepointCase

from odoo.addons.base_rest.controllers.main import (
    RestController,
    _PseudoCollection,
)
from odoo.addons.base_rest.core import _rest_controllers_per_module
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin
from odoo.addons.queue_job.job import Job
from odoo.addons.server_environment import serv_config
from odoo.addons.shopinvader.models.track_external_mixin import (
    TrackExternalMixin,
)

from .. import shopinvader_response


def _install_lang_odoo(env, lang_xml_id):
    lang = env.ref(lang_xml_id)
    wizard = env["base.language.install"].create({"lang": lang.code})
    wizard.lang_install()
    return lang


class UtilsMixin(object):
    def _bind_products(self, products, backend=None):
        backend = backend or self.backend
        bind_wizard_model = self.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_ids": [(6, 0, products.ids)],
                "run_immediately": True,
            }
        )
        bind_wizard.bind_products()

    def _refresh_json_data(self, products, backend=None):
        """Force recomputation of JSON data for given products.

        Especially helpful if your module adds new JSON keys
        but the product are already there and computed w/out your key.
        """
        if not products:
            return
        backend = backend or self.backend
        # TODO: remove hasattr check once `jsonify_stored` is ready.
        # The json-store machinery comes from search engine module.
        # We rely on it for product data BUT only
        # `shopinvader_search_engine` requires that dependency.
        # Hence, tests that need fresh product data because they add
        # new keys to ir.exports record will be broken w/out refresh
        # IF `shopinvader_search_engine` is installed (like on Travis).
        # `jsonify_stored` will extrapolate the feature
        # and allow to get rid of this hack.
        # For full story see
        # https://github.com/shopinvader/odoo-shopinvader/pull/783
        if not hasattr(self.env["shopinvader.variant"], "recompute_json"):
            return
        invader_variants = products
        if invader_variants._name == "product.product":
            invader_variants = products.shopinvader_bind_ids
        invader_variants.filtered_domain(
            [("backend_id", "=", backend.id)]
        ).recompute_json()

    def _install_lang(self, lang_xml_id):
        return _install_lang_odoo(self.env, lang_xml_id)

    @staticmethod
    def _create_invader_partner(env, **kw):
        values = {
            "backend_id": env.ref("shopinvader.backend_1").id,
        }
        values.update(kw)
        return env["shopinvader.partner"].create(values)


class CommonMixin(ComponentMixin, UtilsMixin):
    @staticmethod
    def _setup_backend(cls):
        cls.env = cls.env(context={"lang": "en_US"})
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.precision = cls.env["decimal.precision"].precision_get(
            "Product Price"
        )
        cls.backend.bind_all_product()
        cls.shopinvader_session = {}
        cls.api_key = "myApiKey"
        cls.auth_api_key_name = getattr(
            cls, "AUTH_API_KEY_NAME", "api_key_shopinvader_test"
        )
        if cls.auth_api_key_name not in serv_config.sections():
            serv_config.add_section(cls.auth_api_key_name)
            serv_config.set(cls.auth_api_key_name, "user", "admin")
            serv_config.set(cls.auth_api_key_name, "key", cls.api_key)
        cls.backend.auth_api_key_name = cls.auth_api_key_name
        cls.backend_liege = cls.env.ref("shopinvader.backend_liege")
        cls.company_liege = cls.env.ref("shopinvader.res_company_liege")

    @contextmanager
    def work_on_services(self, **params):
        params = params or {}
        if "shopinvader_backend" not in params:
            params["shopinvader_backend"] = self.backend
        if "shopinvader_session" not in params:
            params["shopinvader_session"] = {}
        if not params.get("partner_user") and params.get("partner"):
            params["partner_user"] = params["partner"]
        if params.get("partner_user"):
            params["invader_partner"] = params[
                "partner_user"
            ]._get_invader_partner(self.backend)
        # Safe defaults as these keys are mandatory for work ctx
        if "partner" not in params:
            params["partner"] = self.env["res.partner"].browse()
        if "partner_user" not in params:
            params["partner_user"] = self.env["res.partner"].browse()
        if "invader_partner" not in params:
            params["invader_partner"] = self.env[
                "shopinvader.partner"
            ].browse()
        collection = _PseudoCollection("shopinvader.backend", self.env)
        yield WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            **params
        )

    def _init_job_counter(self):
        self.existing_job = self.env["queue.job"].search([])

    @property
    def created_jobs(self):
        return self.env["queue.job"].search([]) - self.existing_job

    def _check_nbr_job_created(self, nbr):
        self.assertEqual(len(self.created_jobs), nbr)

    def _perform_created_job(self):
        for job in self.created_jobs:
            Job.load(self.env, job.uuid).perform()
            # self._perform_job(job)

    def _bind_products(self, products, backend=None):
        backend = backend or self.backend
        bind_wizard_model = self.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {"backend_id": backend.id, "product_ids": [(6, 0, products.ids)]}
        )
        bind_wizard.bind_products()

    @classmethod
    def _install_lang(cls, lang_xml_id):
        return _install_lang_odoo(cls.env, lang_xml_id)


class CommonCase(SavepointCase, CommonMixin):

    # by default disable tracking suite-wise, it's a time saver :)
    tracking_disable = True

    @classmethod
    def setUpClass(cls):
        super(CommonCase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=cls.tracking_disable
            )
        )

        class ControllerTest(RestController):
            _root_path = "/test_shopinvader/"
            _collection_name = "shopinvader.backend"
            _default_auth = "public"

        # Force service registration by the creation of a fake controller
        cls._ShopinvaderControllerTest = ControllerTest
        CommonMixin._setup_backend(cls)
        cls.setUpComponent()

    @classmethod
    def tearDownClass(cls):
        super(CommonCase, cls).tearDownClass()
        _rest_controllers_per_module["shopinvader"] = []

    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

        shopinvader_response.set_testmode(True)
        shopinvader_response.get().reset()

        @self.addCleanup
        def cleanupShopinvaderResponseTestMode():
            shopinvader_response.set_testmode(False)

    def _get_selection_label(self, record, field):
        """
        Get the translated label of the record selection field
        :param record: recordset
        :param field: str
        :return: str
        """
        return record._fields.get(field).convert_to_export(
            record[field], record
        )

    def _get_last_external_update_date(self, record):
        if isinstance(record, TrackExternalMixin):
            return record.last_external_update_date
        return False

    def _check_last_external_update_date(self, record, previous_date):
        if isinstance(record, TrackExternalMixin):
            self.assertTrue(record.last_external_update_date > previous_date)


class ProductCommonCase(CommonCase):
    def setUp(self):
        super(ProductCommonCase, self).setUp()
        self.template = self.env.ref(
            "product.product_product_4_product_template"
        )
        self.variant = self.env.ref("product.product_product_4b")
        self.template.taxes_id = self.env.ref("shopinvader.tax_1")
        self.shopinvader_variants = self.env["shopinvader.variant"].search(
            [
                ("record_id", "in", self.template.product_variant_ids.ids),
                ("backend_id", "=", self.backend.id),
            ]
        )
        self.shopinvader_variant = self.env["shopinvader.variant"].search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )


class ShopinvaderRestCase(BaseRestCase):
    AUTH_API_KEY_NAME = "api_key_shopinvader_test"
    AUTH_API_KEY_NAME2 = "api_key_shopinvader_test2"

    def setUp(self, *args, **kwargs):
        super(ShopinvaderRestCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref("shopinvader.backend_1")
        # To ensure multi-backend works correctly, we just have to create
        # a new one on the same company.
        self.backend_copy = self.env.ref("shopinvader.backend_2")
        self.api_key = "myApiKey"
        self.api_key2 = "myApiKey2"
        self.auth_api_key_name = self.AUTH_API_KEY_NAME
        self.auth_api_key_name2 = self.AUTH_API_KEY_NAME2
        if self.auth_api_key_name not in serv_config.sections():
            serv_config.add_section(self.auth_api_key_name)
            serv_config.set(self.auth_api_key_name, "user", "admin")
            serv_config.set(self.auth_api_key_name, "key", self.api_key)
        if self.auth_api_key_name2 not in serv_config.sections():
            serv_config.add_section(self.auth_api_key_name2)
            serv_config.set(self.auth_api_key_name2, "user", "admin")
            serv_config.set(self.auth_api_key_name2, "key", self.api_key2)
        self.backend.auth_api_key_name = self.auth_api_key_name2


class CommonTestDownload(object):
    """
    Dedicated class to test the download service.
    Into your test class, just inherit this one (python mode) and call
    correct function.
    """

    def _test_download_not_allowed(self, service, target):
        """
        Data
            * A target into an invalid/not allowed state
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        with self.assertRaises(MissingError):
            service.download(target.id)

    def _test_download_allowed(self, service, target):
        """
        Data
            * A target with a valid state
        Case:
            * Try to download the document
        Expected result:
            * An http response with the file to download
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        with mock.patch(
            "odoo.addons.shopinvader.services."
            "abstract_download.content_disposition"
        ) as mocked_cd, mock.patch(
            "odoo.addons.shopinvader.services.abstract_download.request"
        ) as mocked_request:
            mocked_cd.return_value = "attachment; filename=test"
            make_response = mock.MagicMock()
            mocked_request.make_response = make_response
            service.download(target.id)
            self.assertEqual(1, make_response.call_count)
            content, headers = make_response.call_args[0]
            self.assertTrue(content)
            self.assertIn(
                ("Content-Disposition", "attachment; filename=test"), headers
            )

    def _test_download_not_owner(self, service, target):
        """
        Data
            * A target into a valid state but doesn't belong to the connected
            user (from the service).
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        self._test_download_not_allowed(service, target)
