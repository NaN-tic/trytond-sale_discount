=======================
Sale Amendment Scenario
=======================

Imports::

    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences

Activate modules::

    >>> config = activate_modules(['sale_discount', 'sale_amendment'])

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create parties::

    >>> Party = Model.get('party.party')
    >>> customer1 = Party(name="Customer 1")
    >>> customer1.save()
    >>> customer2 = Party(name="Customer 2")
    >>> customer2.save()

Create account categories::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.save()

Create products::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')

    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.account_category = account_category
    >>> _ = template.products.new()
    >>> template.save()
    >>> product1, product2 = template.products

Sale first product::

    >>> Sale = Model.get('sale.sale')
    >>> sale = Sale()
    >>> sale.party = customer1
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product1
    >>> sale_line.quantity = 5.0
    >>> sale_line = sale.lines.new()
    >>> sale_line.quantity = 1
    >>> sale_line.product = product1
    >>> sale_line.gross_unit_price = Decimal('10.0000')
    >>> sale_line.discount = Decimal('0.10')
    >>> sale_line.unit_price == Decimal('9.0000')
    True
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product1
    >>> sale_line.quantity = 3.0
    >>> sale_line.amount == Decimal('30.00')
    True
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.state
    'processing'
    >>> sale.revision
    0
    >>> sale.total_amount
    Decimal('89.00')
    >>> len(sale.shipments), len(sale.invoices)
    (1, 1)

Add an amendment::

    >>> amendment = sale.amendments.new()
    >>> line = amendment.lines.new()
    >>> line.action = 'line'
    >>> line.line = sale.lines[0]
    >>> line.product == product1
    True
    >>> line.product = product2
    >>> line.quantity
    5.0
    >>> line.quantity = 4.0
    >>> line.gross_unit_price
    Decimal('10.0000')
    >>> line.discount
    Decimal('0')
    >>> line.unit_price
    Decimal('10.0000')

    >>> line = amendment.lines.new()
    >>> line.action = 'line'
    >>> line.line = sale.lines[1]
    >>> line.gross_unit_price
    Decimal('10.0000')
    >>> line.discount
    Decimal('0.10')
    >>> line.unit_price
    Decimal('9.0000')
    >>> line.discount = Decimal('0.20')
    >>> line.unit_price
    Decimal('8.0000')
    >>> line.gross_unit_price = Decimal('20.0000')
    >>> line.unit_price
    Decimal('16.0000')
    >>> amendment.save()

Validate amendment::

    >>> amendment.click('validate_amendment')
    >>> sale.reload()
    >>> sale.revision
    1
    >>> line = sale.lines[0]
    >>> line.product == product2
    True
    >>> line.quantity
    4.0
    >>> line.gross_unit_price
    Decimal('10.0000')
    >>> line.unit_price
    Decimal('10.0000')
    >>> line = sale.lines[1]
    >>> line.gross_unit_price
    Decimal('20.0000')
    >>> line.unit_price
    Decimal('16.0000')
    >>> line.discount
    Decimal('0.20')
    >>> sale.total_amount
    Decimal('86.00')
