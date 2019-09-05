# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DepositCheque(models.TransientModel):
    _name = "deposit.cheque"

    deposit_date = fields.Date(string='Date of Deposit', default=fields.Date.context_today, required=True)
    bank_id = fields.Many2one('account.bank', string='Bank Name', required=True)

    @api.multi
    def deposit_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        cheque_obj.write({'state': 'deposited', 'deposit_date': self.deposit_date, 'bank_id': self.bank_id.id})


        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_r_id.id
        interim_account = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not interim_account.interim_account_id:
            raise UserError(_('Set Customer Cheque Interim Account under Settings !!!'))
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': interim_account.interim_account_id.id, 'name': '/',
              'partner_id': cheque_obj.partner_id.id,
              'amount_currency': 0.0, 'credit': cheque_obj.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.bank_id.deposit_account.id,
                    'name': cheque_obj.name + ' Clearance', 'amount_currency': 0.0, 'debit': cheque_obj.amount})
        ]
        vals = {
            'journal_id': journal_id,
            'ref': cheque_obj.name,
            'date': self.deposit_date,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        cheque_obj.write(
            {'state': 'deposited', 'deposit_date': self.deposit_date, 'account_move_ids': [(4, account_move.id)], })

