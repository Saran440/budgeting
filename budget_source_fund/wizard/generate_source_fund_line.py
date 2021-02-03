# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class GenerateSourceFundLine(models.TransientModel):
    _name = "generate.source.fund.line"
    _description = "Generate Source of Fund Lines"

    budget_control_ids = fields.Many2many(
        comodel_name="budget.control",
        string="Budget Control",
        required=True,
    )
    date_range_id = fields.Many2one(
        comodel_name="date.range", string="Date Range"
    )
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)

    @api.onchange("date_range_id")
    def _onchange_date_range(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def _check_dates(self, fund):
        if not self.budget_control_ids:
            return
        fund.fund_line_ids.filtered(
            lambda l: l.budget_control_id.id in self.budget_control_ids.ids
        )

    def action_generate_line(self):
        self.ensure_one()
        active_id = self._context.get("active_id", False)
        fund = self.env["budget.source.fund"].browse(active_id)
        # self._check_dates(fund)
        items = [
            (
                0,
                0,
                {
                    "date_range_id": self.date_range_id.id,
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                    "budget_control_id": budget.id,
                    "fund_id": fund.id,
                },
            )
            for budget in self.budget_control_ids
        ]
        fund.write({"fund_line_ids": items})