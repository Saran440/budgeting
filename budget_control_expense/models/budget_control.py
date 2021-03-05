# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BudgetControl(models.Model):
    _inherit = "budget.control"

    amount_expense = fields.Monetary(
        string="Expense",
        compute="_compute_amount_expense",
        help="Sum of expense amount",
    )

    @api.depends("item_ids")
    def _compute_amount_expense(self):
        ExpenseBudgetMove = self.env["expense.budget.move"]
        for rec in self:
            ex_move = ExpenseBudgetMove.search(
                [("analytic_account_id", "=", rec.analytic_account_id.id)]
            )
            amount_expense = sum(ex_move.mapped("debit")) - sum(
                ex_move.mapped("credit")
            )
            rec.amount_expense = amount_expense or 0.0

    def _get_amount_total_commit(self):
        amount_commit = (
            super()._get_amount_total_commit() + self.amount_expense
        )
        return amount_commit