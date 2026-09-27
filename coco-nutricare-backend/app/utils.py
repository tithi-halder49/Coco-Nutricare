from datetime import date


def age_in_months(dob: date, on: date | None = None) -> int:
    on = on or date.today()
    months = (on.year - dob.year) * 12 + (on.month - dob.month)
    if on.day < dob.day:
        months -= 1
    return max(months, 0)


def age_in_months_exact(dob: date, on: date | None = None) -> float:
    on = on or date.today()
    return max((on - dob).days / 30.4375, 0.0)


def age_label(dob: date, on: date | None = None) -> str:
    m = age_in_months(dob, on)
    y, mm = divmod(m, 12)
    if y == 0:
        return f"{mm}m"
    return f"{y}y {mm}m" if mm else f"{y}y"
