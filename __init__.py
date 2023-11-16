# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import amendment
from . import sale
from . import move


def register():
    Pool.register(
        sale.Sale,
        sale.SaleLine,
        move.Move,
        module='sale_discount', type_='model')
    Pool.register(
        amendment.AmendmentLine,
        module='sale_discount', type_='model',
        depends=['sale_amendment'])
