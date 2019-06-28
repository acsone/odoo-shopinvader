# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent
from odoo.tools import float_round


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_shipping(self, cart):
        res = super(AbstractSaleService, self)._convert_shipping(cart)
        selected_carrier = {}
        if cart.carrier_id:
            carrier = cart.carrier_id
            selected_carrier = {
                "id": carrier.id,
                "name": carrier.name,
                "description": carrier.description,
            }
        res.update(
            {
                "amount": {
                    "tax": cart.shipping_amount_tax,
                    "untaxed": cart.shipping_amount_untaxed,
                    "total": cart.shipping_amount_total,
                },
                "selected_carrier": selected_carrier,
            }
        )
        return res

    def _convert_amount(self, sale):
        """
        Inherit to add amounts without shipping prices included
        :param sale: sale.order recordset
        :return: dict
        """
        result = super(AbstractSaleService, self)._convert_amount(sale)
        # Remove the shipping amounts for originals amounts
        shipping_amounts = self._convert_shipping(sale).get("amount", {})
        tax = result.get("tax", 0) - shipping_amounts.get("tax", 0)
        untaxed = result.get("untaxed", 0) - shipping_amounts.get("untaxed", 0)
        total = result.get("total", 0) - shipping_amounts.get("total", 0)
        precision = sale.currency_id.decimal_places
        result.update(
            {
                "tax_without_shipping": float_round(tax, precision),
                "untaxed_without_shipping": float_round(untaxed, precision),
                "total_without_shipping": float_round(total, precision),
            }
        )
        return result

    def _prepare_carrier(self, carrier):
        return {
            "id": carrier.id,
            "name": carrier.name,
            "description": carrier.description,
            "price": carrier.price,
        }

    def _get_available_carrier(self, cart):
        return [
            self._prepare_carrier(carrier)
            for carrier in cart._get_available_carrier()
        ]

    def _is_item(self, line):
        res = super(AbstractSaleService, self)._is_item(line)
        return res and not line.is_delivery
