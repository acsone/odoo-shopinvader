# -*- coding: utf-8 -*-
# © 2020 Acsone (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# shitty code directly lifted from Odoo, I'm not going to rewrite it
# (it was even written by pinky himself)
# flake8: noqa
# pylint: disable=cell-var-from-loop

import fnmatch

from odoo import _, models
from odoo.exceptions import UserError
from odoo.osv import expression

LIKE_COMPARATORS = (
    "like",
    "ilike",
    "=like",
    "=ilike",
    "not ilike",
    "not like",
)


class Base(models.AbstractModel):

    _inherit = "base"

    def partition(self, accessor):
        """Returns a dictionary forming a partition of self into a dictionary
           value/recordset for each value obtained from the accessor.
           The accessor itself can be either a string that can be passed to mapped,
           or an arbitrary function.
           Note that it is always at least as fast to pass a function,
           hence the current implementation.
           If we have a 'field.subfield' accessor such that subfield is not a relational
           then the result is a list (not hashable). Then the str(key) are used.
           In the general case a value could both not be hashable nor stringifiable,
           in a which case this function would crash.
        """
        partition = {}

        if isinstance(accessor, str):
            if "." not in accessor:
                func = lambda r: r[accessor]  # noqa: E731
            else:
                func = lambda r: r.mapped(accessor)  # noqa: E731
        else:
            func = accessor

        for record in self:
            key = func(record)
            if not key.__hash__:
                key = str(key)
            if key not in partition:
                partition[key] = record
            else:
                partition[key] += record

        return partition

    def batch(self, batch_size=None):
        """Yield successive batches of size batch_size, or ."""
        if not (batch_size or "_default_batch_size" in dir(self)):
            raise UserError(
                _(
                    "Either set up a '_default_batch_size' on the model"
                    " or provide a batch_size parameter."
                )
            )
        batch_size = batch_size or self._default_batch_size
        for i in range(0, len(self), batch_size):
            yield self[i : i + batch_size]

    def read_per_record(self, fields=None, load="_classic_read"):
        result = {}
        data_list = self.read(fields=fields, load=load)
        for d in data_list:
            key = d.pop("id")
            result[key] = d
        return result

    def filtered_domain(self, domain):
        """Backport from standard.
        """
        if not domain:
            return self
        result = []
        for d in reversed(domain):
            if d == "|":
                result.append(result.pop() | result.pop())
            elif d == "!":
                result.append(self - result.pop())
            elif d == "&":
                result.append(result.pop() & result.pop())
            elif d == expression.TRUE_LEAF:
                result.append(self)
            elif d == expression.FALSE_LEAF:
                result.append(self.browse())
            else:
                (key, comparator, value) = d
                if key.endswith(".id"):
                    key = key[:-3]
                if key == "id":
                    key = ""
                if key:
                    model = self.browse()
                    for fname in key.split("."):
                        model = model[fname]

                if comparator in LIKE_COMPARATORS:
                    value_esc = (
                        value.replace("_", "?")
                        .replace("%", "*")
                        .replace("[", "?")
                    )
                records = self.browse()
                for rec in self:
                    data = rec.mapped(key)
                    if comparator in ("child_of", "parent_of"):
                        records = data.search(
                            [(data._parent_name, comparator, value)]
                        )
                        value = records.ids
                        comparator = "in"
                    if isinstance(data, models.BaseModel):
                        v = value
                        if isinstance(value, (list, tuple)) and value:
                            v = value[0]
                        if isinstance(v, str):
                            data = data.mapped("display_name")
                        else:
                            data = data.ids if data else [False]
                    if comparator in ("in", "not in"):
                        if not isinstance(value, (list, tuple)):
                            value = [value]

                    if comparator == "=":
                        ok = value in data
                    elif comparator == "in":
                        ok = any(map(lambda x: x in data, value))
                    elif comparator == "<":
                        ok = any(
                            map(lambda x: x is not None and x < value, data)
                        )
                    elif comparator == ">":
                        ok = any(
                            map(lambda x: x is not None and x > value, data)
                        )
                    elif comparator == "<=":
                        ok = any(
                            map(lambda x: x is not None and x <= value, data)
                        )
                    elif comparator == ">=":
                        ok = any(
                            map(lambda x: x is not None and x >= value, data)
                        )
                    elif comparator in ("!=", "<>"):
                        ok = value not in data
                    elif comparator == "not in":
                        ok = all(map(lambda x: x not in data, value))
                    elif comparator == "not ilike":
                        ok = all(
                            map(lambda x: value.lower() not in x.lower(), data)
                        )
                    elif comparator == "ilike":
                        data = [x.lower() for x in data]
                        match = fnmatch.filter(
                            data, "*" + (value_esc or "").lower() + "*"
                        )
                        ok = bool(match)
                    elif comparator == "not like":
                        ok = all(map(lambda x: value not in x, data))
                    elif comparator == "like":
                        ok = bool(
                            fnmatch.filter(
                                data, value and "*" + value_esc + "*"
                            )
                        )
                    elif comparator == "=?":
                        ok = (value in data) or not value
                    elif comparator == "=like":
                        ok = bool(fnmatch.filter(data, value_esc))
                    elif comparator == "=ilike":
                        data = [x.lower() for x in data]
                        ok = bool(
                            fnmatch.filter(data, value and value_esc.lower())
                        )
                    else:
                        raise ValueError
                    if ok:
                        records |= rec
                result.append(records)
        while len(result) > 1:
            result.append(result.pop() & result.pop())
        return result[0]