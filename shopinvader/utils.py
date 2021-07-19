# -*- coding: utf-8 -*-


def get_partner_work_context(shopinvader_partner):
    """Retrieve service work context for given shopinvader.partner"""
    ctx = {}
    ctx["invader_partner"] = shopinvader_partner
    ctx["invader_partner_user"] = shopinvader_partner
    # TODO: `partner` and `partner_user` could be abandoned as soon as
    # all `shopinvader` modules stop relying on `self.partner`.
    partner_user = shopinvader_partner.record_id
    ctx["partner_user"] = partner_user
    # The partner user for the main account or for sale order may differ.
    partner_shop = partner_user.get_shop_partner(
        shopinvader_partner.backend_id
    )
    ctx["partner"] = partner_shop
    if partner_shop != partner_user:
        # Invader partner must represent the same partner as the shop
        invader_partner_shop = partner_shop._get_invader_partner(
            shopinvader_partner.backend_id
        )
        if invader_partner_shop:
            ctx["invader_partner"] = invader_partner_shop
    return ctx
