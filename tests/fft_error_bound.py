"""Evaluate the stated radix-2 error bounds with ample decimal precision."""
from decimal import Decimal, localcontext

with localcontext() as context:
    context.prec = 100
    u = Decimal(2) ** -53
    beta = 8 * u
    for name, levels, norm_product, limit in [
        ('integer', 22, Decimal('2e12'), Decimal('0.166')),
        ('modular limb', 19, Decimal(2047)**2 * (Decimal(2)**18 + 1), Decimal('0.079')),
    ]:
        bound = norm_product * (
            (1 + u)**(3*levels)
            * (1 + Decimal(5).sqrt()*u)**(3*levels + 1)
            * (1 + beta)**(3*levels) - 1
        )
        assert bound < limit < Decimal('0.5')
        print(f'{name}: worst-case absolute error < {limit}; evaluated {bound:.12f} PASS')
