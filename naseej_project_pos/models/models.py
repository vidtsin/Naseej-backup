# -*- coding: utf-8 -*-
from addons.account.models.account_bank_statement import AccountBankStatement
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import Warning, UserError


class NaseejAccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_later = fields.Boolean('partial payment')


class NaseejPosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def action_pos_session_closing_control(self):
        for session in self:
            for statement in session.statement_ids:
                if statement.journal_id.payment_later:
                    statement.unlink()

                else:
                    self._check_pos_session_balance()
                    session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
                    if not session.config_id.cash_control:
                        session.action_pos_session_close()

