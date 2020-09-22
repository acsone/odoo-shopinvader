# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields
from odoo.tests import Form

from .common import CommonCase, CommonTestDownload


class TestInvoice(CommonCase, CommonTestDownload):
    @classmethod
    def setUpClass(cls):
        super(TestInvoice, cls).setUpClass()
        cls.register_payments_obj = cls.env["account.register.payments"]
        cls.journal_obj = cls.env["account.journal"]
        cls.sale = cls.env.ref("shopinvader.sale_order_2")
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        cls.bank_journal_euro = cls.journal_obj.create(
            {"name": "Bank", "type": "bank", "code": "BNK627"}
        )
        cls.invoice_obj = cls.env["account.invoice"]
        cls.invoice = cls._confirm_and_invoice_sale(cls, cls.sale)
        cls.non_sale_invoice = cls._create_invoice(cls, cls.partner)
        cls.non_sale_invoice.action_invoice_open()
        # set the layout on the company to be sure that the print action
        # will not display the document layout configurator
        cls.env.user.company_id.external_report_layout_id = cls.env.ref(
            "web.external_layout_standard"
        ).id

    def setUp(self, *args, **kwargs):
        super(TestInvoice, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.sale_service = work.component(usage="sales")
            self.invoice_service = work.component(usage="invoice")

    def _make_payment(self, invoice):
        """
        Make the invoice payment
        :param invoice: account.invoice recordset
        :return: bool
        """
        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
        wizard_obj = self.register_payments_obj.with_context(ctx)
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        register_payments.create_payments()

    def _confirm_and_invoice_sale(self, sale):
        sale.action_confirm()
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        invoice_id = sale.action_invoice_create()
        invoice = self.env["account.invoice"].browse(invoice_id)
        invoice.action_invoice_open()
        invoice.action_move_create()
        return invoice

    def _create_invoice(self, partner, **kw):
        product = self.env.ref("product.product_product_4")
        form = Form(self.invoice_obj)
        form.partner_id = partner
        for k, v in kw.items():
            setattr(form, k, v)
        with form.invoice_line_ids.new() as line:
            line.product_id = product
        invoice = form.save()
        return invoice

    def test_01(self):
        """
        Data
            * A confirmed sale order with an invoice not yet paid
        Case:
            * Try to download the image
        Expected result:
            * MissingError should be raised
        """
        self._test_download_not_allowed(self.invoice_service, self.invoice)

    def test_02(self):
        """
        Data
            * A confirmed sale order with a paid invoice
        Case:
            * Try to download the image
        Expected result:
            * An http response with the file to download
        """
        self._make_payment(self.invoice)
        self._test_download_allowed(self.invoice_service, self.invoice)

    def test_03(self):
        """
        Data
            * A confirmed sale order with a paid invoice but not for the
            current customer
        Case:
            * Try to download the image
        Expected result:
            * MissingError should be raised
        """
        sale = self.env.ref("sale.sale_order_1")
        sale.shopinvader_backend_id = self.backend
        self.assertNotEqual(sale.partner_id, self.partner)
        invoice = self._confirm_and_invoice_sale(sale)
        self._make_payment(invoice)
        self._test_download_not_owner(self.invoice_service, self.invoice)

    def test_domain_01(self):
        # By default include only invoices related to sales
        self.assertTrue(self.backend.invoice_linked_to_sale_only)
        # and only paid invoice are accessible
        self.assertFalse(self.backend.invoice_access_open)
        # Invoices are open, none of them is included
        self.assertEqual(self.invoice.state, "open")
        self.assertEqual(self.non_sale_invoice.state, "open")
        domain = self.invoice_service._get_base_search_domain()
        self.assertNotIn(
            self.non_sale_invoice, self.invoice_obj.search(domain)
        )
        self.assertNotIn(self.invoice, self.invoice_obj.search(domain))
        # pay both invoices
        self._make_payment(self.invoice)
        self._make_payment(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        # Extra invoice still not found
        self.assertNotIn(
            self.non_sale_invoice, self.invoice_obj.search(domain)
        )
        self.assertIn(self.invoice, self.invoice_obj.search(domain))

    def test_domain_02(self):
        # Include extra invoices
        self.backend.invoice_linked_to_sale_only = False
        # and only paid invoice are accessible
        self.assertFalse(self.backend.invoice_access_open)
        # Invoices are open, none of them is included
        self.assertEqual(self.invoice.state, "open")
        self.assertEqual(self.non_sale_invoice.state, "open")
        domain = self.invoice_service._get_base_search_domain()
        self.assertNotIn(
            self.non_sale_invoice, self.invoice_obj.search(domain)
        )
        self.assertNotIn(self.invoice, self.invoice_obj.search(domain))
        # pay both invoices
        self._make_payment(self.invoice)
        self._make_payment(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        # Extra invoice available now as well
        self.assertIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))

    def test_domain_03(self):
        # Include extra invoices
        self.backend.invoice_linked_to_sale_only = False
        # and open invoices enabled as well
        self.backend.invoice_access_open = True
        # Invoices are open, none of them is included
        self.assertEqual(self.invoice.state, "open")
        self.assertEqual(self.non_sale_invoice.state, "open")
        domain = self.invoice_service._get_base_search_domain()
        self.assertIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))
        # pay both invoices
        self._make_payment(self.invoice)
        self._make_payment(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        # Still both available
        self.assertIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))

    def test_report_get(self):
        default_report = self.env.ref("account.account_invoices")
        self.assertEqual(
            self.invoice_service._get_report_action(self.invoice),
            default_report.report_action(self.invoice, config=False),
        )
        # set a custom report
        custom = default_report.copy({"name": "My custom report"})
        self.backend.invoice_report_id = custom
        self.assertEqual(
            self.invoice_service._get_report_action(self.invoice)["name"],
            "My custom report",
        )
