# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class BudgetControl(models.Model):
    _inherit = "budget.control"

    plan_id = fields.Many2one(
        comodel_name="budget.plan",
        index=True,
    )