# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class BudgetControl(models.Model):
    _inherit = "budget.control"

    allocated_amount = fields.Monetary(
        help="Initial total amount for transfer",
    )
    released_amount = fields.Monetary(
        compute="_compute_allocated_released_amount",
        store=True,
        help="Total amount for transfer current",
    )

    @api.depends("allocated_amount")
    def _compute_allocated_released_amount(self):
        for rec in self:
            rec.released_amount = rec.allocated_amount

    def _get_amount_available(self):
        self.ensure_one()
        plan_amount = sum(self.item_ids.mapped("amount"))
        fund_amount = self.released_amount
        return plan_amount, fund_amount

    def _compare_plan_fund(self, plan_amount, fund_amount):
        """ Check total amount plan have to less than or equal to released amount """
        amount_compare = (
            float_compare(
                plan_amount,
                fund_amount,
                precision_rounding=self.currency_id.rounding,
            )
            == 1
        )
        message = _(
            "you have to plan total amount is "
            "less than or equal to {:,.2f} {}".format(
                fund_amount, self.currency_id.symbol
            )
        )
        return amount_compare, message

    @api.constrains("state")
    def _check_fund_amount(self):
        for rec in self:
            plan_amount, fund_amount = rec._get_amount_available()
            amount_compare, message = rec._compare_plan_fund(
                plan_amount, fund_amount
            )
            if rec.state == "done" and amount_compare:
                raise UserError(message)