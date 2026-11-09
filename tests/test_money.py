from decimal import Decimal

import pytest

from app.money import RefundExceedsOrder, cents_to_yuan, check_refund, yuan_to_cents


@pytest.mark.parametrize(
    "cents,expected",
    [(0, "0.00"), (5, "0.05"), (100, "1.00"), (12900, "129.00"), (777, "7.77"), (99, "0.99")],
)
def test_cents_to_yuan(cents, expected):
    assert cents_to_yuan(cents) == expected


@pytest.mark.parametrize(
    "amount,cents",
    [("1.00", 100), ("0.1", 10), ("129.999", 13000), (Decimal("7.775"), 778), (3, 300)],
)
def test_yuan_to_cents_rounds_half_up(amount, cents):
    assert yuan_to_cents(amount) == cents


def test_round_trip():
    assert yuan_to_cents(cents_to_yuan(12345)) == 12345


def test_refund_cannot_exceed_order():
    with pytest.raises(RefundExceedsOrder):
        check_refund(1000, 1001)


def test_refund_equal_to_order_is_allowed():
    check_refund(1000, 1000)


def test_negative_refund_rejected():
    with pytest.raises(RefundExceedsOrder):
        check_refund(1000, -1)
