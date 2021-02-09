# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class BudgetPlan(models.Model):
    _name = "budget.plan"
    _inherit = ["mail.thread"]
    _description = "Source of Fund Group"

    name = fields.Char(required=True, tracking=True)
    budget_period_id = fields.Many2one(
        comodel_name="budget.period",
        required=True,
    )
    fund_plan_line = fields.One2many(
        comodel_name="budget.source.fund.plan",
        inverse_name="plan_id",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    def action_generate_plan(self):
        self.ensure_one()
        SourceFundPlan = self.env["budget.source.fund.plan"]
        fund_plan = SourceFundPlan.search(
            [
                ("budget_period_id", "=", self.budget_period_id.id),
                ("state", "=", "done"),
            ]
        )
        fund_plan.write({"plan_id": self.id})
        return fund_plan

    def action_plan_generate_budget_control(self):
        analytic_plan = self.mapped("fund_plan_line.allocation_line").mapped(
            "analytic_account_id"
        )
        return {
            "name": _("Generate Budget Control Sheet"),
            "res_model": "generate.budget.control",
            "view_mode": "form",
            "context": {
                "active_model": "budget.plan",
                "active_ids": self.ids,
                "default_analytic_account_ids": analytic_plan.ids,
            },
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def action_done(self):
        self.write({"state": "done"})
        return True

    def action_cancel(self):
        self.write({"state": "cancel"})
        return True

    def action_draft(self):
        self.write({"state": "draft"})
        return True
