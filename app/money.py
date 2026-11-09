"""金额处理：内部一律整数分，对外一律两位小数字符串。"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


class RefundExceedsOrder(ValueError):
    """退款金额超过订单金额。"""


def cents_to_yuan(cents: int) -> str:
    value = (Decimal(int(cents)) / Decimal(100)).quantize(CENT, rounding=ROUND_HALF_UP)
    return f"{value:.2f}"


def yuan_to_cents(amount: str | int | Decimal) -> int:
    value = Decimal(str(amount)).quantize(CENT, rounding=ROUND_HALF_UP)
    return int((value * 100).to_integral_value(rounding=ROUND_HALF_UP))


def check_refund(total_cents: int, refunded_cents: int) -> None:
    if refunded_cents < 0:
        raise RefundExceedsOrder("退款金额不能为负")
    if refunded_cents > total_cents:
        raise RefundExceedsOrder(
            f"退款金额 {cents_to_yuan(refunded_cents)} 超过订单金额 {cents_to_yuan(total_cents)}"
        )
