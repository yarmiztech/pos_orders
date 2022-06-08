from datetime import datetime, timedelta

from odoo import models, fields, api


class DayBook(models.Model):
    _name = 'day.book'

    current_date = datetime.now()
    from_date = fields.Datetime('From Date', default=current_date-timedelta(days=1))
    to_date = fields.Datetime('To Date', default=datetime.now())

    one_to_many = fields.One2many('day.book.lines', 'many_to_one')

    @api.onchange('from_date', 'to_date')
    def get_sessions_onchange(self):
        data = self.env['pos.session'].search([
            ('start_at', '>=', self.from_date),
            ('stop_at', '<=', self.to_date)
        ])
        data_list = []
        for session in data:
            cash_sum = 0.0
            bank_sum = 0.0

            for order in session.order_ids:
                for line in order.payment_ids:
                    if line.payment_method_id.is_cash_count:
                        cash_sum += line.amount
                    else:
                        bank_sum += line.amount

            values = (0, 0, {
                'sessions': session.name,
                'opening_time': session.start_at,
                'closing_time': session.stop_at,
                'customer_count': session.order_count,
                'cash': cash_sum,
                'bank': bank_sum,
                'total': cash_sum + bank_sum,
            })
            data_list.append(values)

        self.one_to_many = None
        self.one_to_many = data_list

        @api.model
        def get_sessions_by_default(self):
            data = self.env['pos.session'].search([
                ('start_at', '>=', self.from_date),
                ('stop_at', '<=', self.to_date)
            ])
            data_list = []
            for session in data:
                cash_sum = 0.0
                bank_sum = 0.0

                for order in session.order_ids:
                    for line in order.payment_ids:
                        if line.payment_method_id.is_cash_count:
                            cash_sum += line.amount
                        else:
                            bank_sum += line.amount

                values = (0, 0, {
                    'sessions': session.name,
                    'opening_time': session.start_at,
                    'closing_time': session.stop_at,
                    'customer_count': session.order_count,
                    'cash': cash_sum,
                    'bank': bank_sum,
                    'total': cash_sum + bank_sum,
                })
                data_list.append(values)

            self.one_to_many = None
            self.one_to_many = data_list

    def get_session_data(self, session_lines):
        # here session_lines is the one2many data which has many fields
        print(session_lines.sessions)

        data = self.env['pos.session'].search([('name', '=', session_lines.sessions)])
        return data
        # for session in data:
        #     print(session.name)
        #     for prod in order.lines:
        #         print(prod.full_product_name)

        # return [
        #     # {'category': "Foo", },
        #     # {'category': "Bar"},
        #     # {'category': "Qux"},
        #     # {'category': "FooQux"},
        #     # {'category': "Foobar"},
        # ]
    def get_pos_categ_amount(self, product, categ_id):
        amount = 0.0
        for order in product.order_ids:
            for line in order.lines:
                if line.product_id.pos_categ_id == categ_id:
                    amount += line.price_subtotal_incl
        return '{:.2f}'.format(amount)

    def get_pos_categ_quantity(self, product, categ_id):
        quantity = 0.0
        for order in product.order_ids:
            for line in order.lines:
                if line.product_id.pos_categ_id == categ_id:
                    quantity += line.qty
        return '{:.2f}'.format(quantity)

    def get_session_discount(self, product):
        total_discount = 0.00
        for line in product.one_to_many:
            data = self.env['pos.session'].search([('name', '=', line.sessions)])
            total_discount += data.total_discount
        return total_discount


class DayBookLines(models.Model):
    _name = 'day.book.lines'

    sessions = fields.Char('Sessions')
    opening_time = fields.Datetime('Opening Time')
    closing_time = fields.Datetime('Closing Time')
    customer_count = fields.Float('Customer Count')
    cash = fields.Float('Cash')
    bank = fields.Float('Bank')
    total = fields.Float('Total Value')

    many_to_one = fields.Many2one('day.book')

