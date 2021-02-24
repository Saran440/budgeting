# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BudgetControl(models.Model):
    _inherit = "budget.control"

    amount_purchase_request = fields.Monetary(
        string="Purchase Request",
        compute="_compute_amount_purchase_request",
        help="Sum of purchase amount",
    )

    @api.depends("item_ids")
    def _compute_amount_purchase_request(self):
        PurchaseBudgetMove = self.env["purchase.request.budget.move"]
        for rec in self:
            pr_move = PurchaseBudgetMove.search(
                [("analytic_account_id", "=", rec.analytic_account_id.id)]
            )
            amount_purchase_request = sum(pr_move.mapped("debit")) - sum(
                pr_move.mapped("credit")
            )
            rec.amount_purchase_request = amount_purchase_request or 0.0

    def _get_amount_total_commit(self):
        amount_commit = (
            super()._get_amount_total_commit() + self.amount_purchase_request
        )
        return amount_commit
