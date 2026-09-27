"""
WHO weight-for-age growth analysis using the LMS method.

IMPORTANT: the built-in table below is a COARSE approximation (yearly points,
interpolated) for development/demo only. For real use, download the official
WHO Child Growth Standards weight-for-age tables (boys & girls, columns
Month,L,M,S) and point WHO_WFA_BOYS_CSV / WHO_WFA_GIRLS_CSV at them.
"""
import csv
import math
from functools import lru_cache

from ..config import settings
from ..models import Child, Gender
from ..utils import age_in_months_exact

# month: (L, M, S) -- approximate, 0-60 months
_BOYS_APPROX = {
    0: (0.3487, 3.3464, 0.14602), 6: (0.1257, 7.9340, 0.11080), 12: (0.0644, 9.6479, 0.10925),
    24: (-0.0137, 12.1515, 0.11426), 36: (-0.0689, 14.3429, 0.12191),
    48: (-0.1172, 16.3489, 0.12850), 60: (-0.1600, 18.3366, 0.13394),
}
_GIRLS_APPROX = {
    0: (0.3809, 3.2322, 0.14171), 6: (-0.0756, 7.2970, 0.12204), 12: (-0.2024, 8.9481, 0.12268),
    24: (-0.2941, 11.4775, 0.12996), 36: (-0.3549, 13.8503, 0.13624),
    48: (-0.3970, 16.0697, 0.14198), 60: (-0.4290, 18.2193, 0.14765),
}

DISCLAIMER = "This alert does not diagnose a condition. Consult your pediatrician."


@lru_cache
def _load_csv(path: str) -> dict[int, tuple[float, float, float]]:
    table = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            table[int(float(row["Month"]))] = (float(row["L"]), float(row["M"]), float(row["S"]))
    return table


def _table(gender: Gender) -> tuple[dict, bool]:
    path = settings.WHO_WFA_BOYS_CSV if gender == Gender.male else settings.WHO_WFA_GIRLS_CSV
    if path:
        return _load_csv(path), True
    return (_BOYS_APPROX if gender == Gender.male else _GIRLS_APPROX), False


def _lms_at(table: dict, months: float):
    keys = sorted(table)
    if months < keys[0] or months > keys[-1]:
        return None
    for lo, hi in zip(keys, keys[1:]):
        if lo <= months <= hi:
            t = (months - lo) / (hi - lo)
            return tuple(a + (b - a) * t for a, b in zip(table[lo], table[hi]))
    return table[keys[-1]]


def weight_z_score(weight_kg: float, months: float, gender: Gender) -> float | None:
    table, _ = _table(gender)
    lms = _lms_at(table, months)
    if not lms:
        return None
    L, M, S = lms
    if abs(L) < 1e-9:
        return math.log(weight_kg / M) / S
    return ((weight_kg / M) ** L - 1) / (L * S)


def z_to_percentile(z: float) -> float:
    return round(50 * (1 + math.erf(z / math.sqrt(2))), 1)


def analyze_growth(child: Child) -> dict:
    _, official = _table(child.gender)
    history = []
    for m in sorted(child.measurements, key=lambda x: x.measured_on):
        months = age_in_months_exact(child.date_of_birth, m.measured_on)
        z = weight_z_score(m.weight_kg, months, child.gender)
        history.append({
            "measured_on": m.measured_on, "weight_kg": m.weight_kg, "height_cm": m.height_cm,
            "age_months": round(months, 1),
            "z_score": round(z, 2) if z is not None else None,
            "percentile": z_to_percentile(z) if z is not None else None,
        })

    first_name = child.name.split()[0]
    alerts: list[str] = []
    trend = "no_data" if not history else "normal"
    latest = history[-1] if history else None

    if latest and latest["percentile"] is not None:
        if latest["percentile"] < 3:
            alerts.append(f"{first_name}'s weight is below the 3rd percentile for age.")
        elif latest["percentile"] > 97:
            alerts.append(f"{first_name}'s weight is above the 97th percentile for age.")

    if len(history) >= 2:
        prev, last = history[-2], history[-1]
        if last["weight_kg"] < prev["weight_kg"]:
            alerts.append(f"{first_name}'s weight has decreased since the last measurement.")
        elif prev["z_score"] is not None and last["z_score"] is not None \
                and prev["z_score"] - last["z_score"] >= 1.0:
            alerts.append(f"{first_name}'s weight gain has slowed down.")

    if alerts:
        trend = "needs_review"

    note = "Official WHO LMS tables loaded." if official else \
        "Using approximate built-in WHO reference (0-5 years). Load official WHO tables for clinical use."
    if latest and latest["percentile"] is None:
        note += " Percentile unavailable for this age range."

    return {
        "child_id": child.id, "child_name": child.name,
        "current_weight_kg": child.weight_kg, "current_height_cm": child.height_cm,
        "who_percentile": latest["percentile"] if latest else None,
        "trend": trend, "alerts": alerts, "history": history,
        "reference_note": note, "disclaimer": DISCLAIMER,
    }
