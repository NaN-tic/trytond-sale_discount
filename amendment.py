# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.modules.account_invoice_discount.invoice import (gross_unit_price_digits,
    discount_digits)
from trytond.modules.product import round_price

STATES={
    'readonly': Eval('state') != 'draft',
    'invisible': Eval('action') != 'line',
    'required': Eval('action') == 'line',
    }


class AmendmentLine(metaclass=PoolMeta):
    __name__ = 'sale.amendment.line'
    gross_unit_price = fields.Numeric('Gross Price', digits=gross_unit_price_digits,
        states=STATES, depends=['state', 'action'])
    discount = fields.Numeric('Discount', digits=discount_digits,
        states=STATES, depends=['state', 'action'])

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.unit_price.states['readonly'] = True

    @fields.depends(methods=['update_prices'])
    def on_change_gross_unit_price(self):
        return self.update_prices()

    @fields.depends('unit_price', methods=['update_prices'])
    def on_change_unit_price(self):
        # unit_price has readonly state but could set unit_price from source code
        if self.unit_price is not None:
            self.update_prices()

    @fields.depends(methods=['update_prices'])
    def on_change_discount(self):
        return self.update_prices()

    @fields.depends('line')
    def on_change_line(self):
        super().on_change_line()
        if self.line:
            self.gross_unit_price = self.line.gross_unit_price
            self.discount = self.line.discount
        else:
            self.gross_unit_price = None
            self.discount = None

    def _apply_line(self, sale, sale_line):
        super()._apply_line(sale, sale_line)
        sale_line.gross_unit_price = self.gross_unit_price
        sale_line.discount = self.discount

    @fields.depends('gross_unit_price', 'unit_price', 'discount')
    def update_prices(self):
        unit_price = None
        gross_unit_price = self.gross_unit_price
        if self.gross_unit_price is not None and self.discount is not None:
            unit_price = self.gross_unit_price * (1 - self.discount)
            unit_price = round_price(unit_price)

            if self.discount != 1:
                gross_unit_price = unit_price / (1 - self.discount)

            gup_digits = self.__class__.gross_unit_price.digits[1]
            gross_unit_price = gross_unit_price.quantize(
                Decimal(str(10.0 ** -gup_digits)))

        self.gross_unit_price = gross_unit_price
        self.unit_price = unit_price
