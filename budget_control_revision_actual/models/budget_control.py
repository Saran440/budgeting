# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BudgetControl(models.Model):
    _inherit = "budget.control"

    def _update_actual_value(self, item_ids, budget_moves):
        bm_nogroup = budget_moves.copy()
        for item in item_ids:
            activity_group = item.activity_group_id.id
            amount_consumed = 0.0
            for key, bm in budget_moves.items():
                all_budget_move = bm.filtered(
                    lambda l: l.activity_id.activity_group_id.id
                    == activity_group
                    and item.date_from <= l.date <= item.date_to
                )
                if all_budget_move:
                    bm_nogroup[key] -= all_budget_move
                    amount_consumed += sum(bm.mapped("debit"))
            item.write({"amount": amount_consumed})
        return bm_nogroup

    def _get_consumed_plan(self, date):
        self.ensure_one()
        MISReport = kpi = self.env["mis.report.kpi"]
        # Find Budget Move range before current month
        first_month_day = date.replace(day=1)
        domain = [
            ("analytic_account_id", "=", self.analytic_account_id.id),
            ("not_affect_budget", "=", False),
            ("date", "<", first_month_day),
        ]
        account_budget_move = self.get_budget_move(
            doc_type="account", domain=domain
        )
        domain_commit = [
            ("analytic_account_id", "=", self.analytic_account_id.id),
            ("date", "<", first_month_day),
        ]
        commit_budget_move = self.get_budget_move(
            doc_type="commit", domain=domain_commit
        )
        budget_move = commit_budget_move
        budget_move["account_budget_move"] = account_budget_move
        # Filter date range before current month
        item_ids = self.item_ids.filtered(
            lambda l: l.date_from < first_month_day
        )
        item_ids.write({"amount": 0.0})
        bm_nogroup = self._update_actual_value(item_ids, budget_move)
        # Case used activity group other plan
        for key, bm in bm_nogroup.items():
            if bm and bm != budget_move[key]:
                ag_id = bm.mapped("activity_id.activity_group_id")
                kpi_ids = MISReport.search(
                    [("budget_activity_group", "in", ag_id.ids)]
                )
                kpi += kpi_ids

        if kpi:
            ctx = {"skip_unlink": True, "kpi_ids": list(set(kpi.ids))}
            self.sudo().with_context(ctx).prepare_budget_control_matrix()
            item_new_ids = self.item_ids.filtered(
                lambda l: l.date_from < first_month_day
                and l.activity_group_id in kpi.mapped("budget_activity_group")
            )
            bm_nogroup = self._update_actual_value(item_new_ids, budget_move)
        return bm_nogroup

    def action_update_actual_plan(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        date = self._context.get("manual_date", today)
        self._get_consumed_plan(date)
        return True