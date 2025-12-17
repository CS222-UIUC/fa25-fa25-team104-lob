from decimal import Decimal, ROUND_HALF_UP

USD_SCALE = 100            # cents per USD
INST_SCALE = 1_000_000     # microunits per instrument (adjust if needed)


def D(x) -> Decimal:
    return Decimal(str(x))


def price_to_cents(price) -> int:
    """Convert a decimal price (e.g. 101.50) to integer cents using HALF_UP."""
    p = D(price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((p * USD_SCALE).to_integral_value())


def cents_to_usd_str(cents: int) -> str:
    return f"{(D(cents) / USD_SCALE):f}"


def inst_to_micro(qty) -> int:
    """Convert instrument quantity to integer microunits using HALF_UP."""
    q = D(qty)
    return int((q * INST_SCALE).to_integral_value(rounding=ROUND_HALF_UP))


def micro_to_inst_str(micro: int) -> str:
    return f"{(D(micro) / INST_SCALE):f}"


def required_hold_cents_ceil(price_cents: int, qty_micro: int, inst_scale: int = INST_SCALE) -> int:
    """
    Conservative ceil of (price_cents * qty_micro / inst_scale).
    Ensures reserved cents always cover possible settlement amount.
    """
    num = price_cents * qty_micro
    return (num + inst_scale - 1) // inst_scale


def settle_amount_cents(price_cents: int, qty_micro: int, inst_scale: int = INST_SCALE) -> int:
    """
    Compute settlement amount in cents for given price_cents and qty_micro,
    rounding HALF_UP by doing integer nearest division.
    """
    # nearest integer division: (num + inst_scale//2) // inst_scale
    num = price_cents * qty_micro
    return (num + inst_scale // 2) // inst_scale


# Utility helpers for integer-only pricing/quantities.
def price_times_qty_to_cents(price_cents: int, qty_units: int) -> int:
    """Exact integer multiplication: price in cents * quantity in whole units -> cents."""
    return int(price_cents) * int(qty_units)


def validate_non_negative_int(v) -> int:
    """Validate and return a non-negative integer."""
    iv = int(v)
    if iv < 0:
        raise ValueError("value must be non-negative")
    return iv