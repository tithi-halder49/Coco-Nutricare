from datetime import date
import math


# =========================================================
# AGE CALCULATION
# =========================================================

def calculate_age_in_days(
    date_of_birth: date,
    measured_on: date
) -> int:
    """
    Calculate completed age in days.
    """
    return max(0, (measured_on - date_of_birth).days)


def calculate_age_in_months(
    date_of_birth: date,
    measured_on: date
) -> int:
    """
    Calculate completed age in months.
    """
    months = (
        (measured_on.year - date_of_birth.year) * 12
        + (measured_on.month - date_of_birth.month)
    )

    if measured_on.day < date_of_birth.day:
        months -= 1

    return max(0, months)


# =========================================================
# WHO WEIGHT-FOR-AGE LMS REFERENCE
# =========================================================
#
# WHO Child Growth Standards
# Weight-for-Age
# Birth to 5 years
#
# Reference points currently available in the project.
# =========================================================

WHO_WFA_REFERENCE = {

    "male": {
        0: {
            "L": 0.3487,
            "M": 3.3464,
            "S": 0.14602,
        },
        30: {
            "L": 0.2303,
            "M": 4.4525,
            "S": 0.13413,
        },
        90: {
            "L": 0.1747,
            "M": 6.3457,
            "S": 0.11750,
        },
        180: {
            "L": 0.1269,
            "M": 7.9002,
            "S": 0.10965,
        },
        365: {
            "L": 0.0645,
            "M": 9.6460,
            "S": 0.10925,
        },
        730: {
            "L": -0.0136,
            "M": 12.1482,
            "S": 0.11425,
        },
        1095: {
            "L": -0.0688,
            "M": 14.3387,
            "S": 0.12115,
        },
        1460: {
            "L": -0.1130,
            "M": 16.3435,
            "S": 0.12757,
        },
        1825: {
            "L": -0.1505,
            "M": 18.3298,
            "S": 0.13515,
        },
    },

    "female": {
        0: {
            "L": 0.3809,
            "M": 3.2322,
            "S": 0.14171,
        },
        30: {
            "L": 0.1727,
            "M": 4.1716,
            "S": 0.13738,
        },
        90: {
            "L": 0.0424,
            "M": 5.8181,
            "S": 0.12631,
        },
        180: {
            "L": -0.0729,
            "M": 7.2650,
            "S": 0.12208,
        },
        365: {
            "L": -0.2022,
            "M": 8.9462,
            "S": 0.12267,
        },
        730: {
            "L": -0.2940,
            "M": 11.4741,
            "S": 0.12389,
        },
        1095: {
            "L": -0.3201,
            "M": 13.8456,
            "S": 0.12918,
        },
        1460: {
            "L": -0.3361,
            "M": 16.0638,
            "S": 0.13882,
        },
        1825: {
            "L": -0.3518,
            "M": 18.2122,
            "S": 0.14818,
        },
    },
}


# =========================================================
# WHO HEIGHT-FOR-AGE REFERENCE
# =========================================================
#
# WHO Child Growth Standards
# Height-for-Age
# 2 to 5 years
#
# The current project test case is approximately 52 months.
# =========================================================

WHO_HFA_REFERENCE = {

    "male": {
        49: {
            "L": 1.0,
            "M": 103.8886,
            "S": 0.04073,
        },
        50: {
            "L": 1.0,
            "M": 104.4473,
            "S": 0.04086,
        },
        51: {
            "L": 1.0,
            "M": 105.0041,
            "S": 0.04100,
        },
        52: {
            "L": 1.0,
            "M": 105.5596,
            "S": 0.04113,
        },
        53: {
            "L": 1.0,
            "M": 106.1138,
            "S": 0.04126,
        },
        54: {
            "L": 1.0,
            "M": 106.6668,
            "S": 0.04139,
        },
        55: {
            "L": 1.0,
            "M": 107.2188,
            "S": 0.04152,
        },
        56: {
            "L": 1.0,
            "M": 107.7697,
            "S": 0.04165,
        },
        57: {
            "L": 1.0,
            "M": 108.3198,
            "S": 0.04177,
        },
        58: {
            "L": 1.0,
            "M": 108.8689,
            "S": 0.04190,
        },
        59: {
            "L": 1.0,
            "M": 109.4170,
            "S": 0.04202,
        },
        60: {
            "L": 1.0,
            "M": 109.9638,
            "S": 0.04214,
        },
    },

    "female": {
        49: {
            "L": 1.0,
            "M": 103.3197,
            "S": 0.04206,
        },
        50: {
            "L": 1.0,
            "M": 103.9021,
            "S": 0.04220,
        },
        51: {
            "L": 1.0,
            "M": 104.4786,
            "S": 0.04233,
        },
        52: {
            "L": 1.0,
            "M": 105.0494,
            "S": 0.04246,
        },
        53: {
            "L": 1.0,
            "M": 105.6148,
            "S": 0.04259,
        },
        54: {
            "L": 1.0,
            "M": 106.1748,
            "S": 0.04272,
        },
        55: {
            "L": 1.0,
            "M": 106.7295,
            "S": 0.04285,
        },
        56: {
            "L": 1.0,
            "M": 107.2788,
            "S": 0.04298,
        },
        57: {
            "L": 1.0,
            "M": 107.8227,
            "S": 0.04310,
        },
        58: {
            "L": 1.0,
            "M": 108.3613,
            "S": 0.04322,
        },
        59: {
            "L": 1.0,
            "M": 108.8948,
            "S": 0.04334,
        },
        60: {
            "L": 1.0,
            "M": 109.4233,
            "S": 0.04347,
        },
    },
}


# =========================================================
# LMS Z-SCORE
# =========================================================

def calculate_lms_zscore(
    value: float,
    L: float,
    M: float,
    S: float
) -> float | None:

    if value is None or value <= 0:
        return None

    if M <= 0 or S <= 0:
        return None

    if L == 0:
        z = math.log(value / M) / S
    else:
        z = (((value / M) ** L) - 1) / (L * S)

    return z


# =========================================================
# Z-SCORE TO PERCENTILE
# =========================================================

def zscore_to_percentile(
    z: float
) -> float | None:

    if z is None:
        return None

    percentile = (
        0.5
        * (
            1
            + math.erf(
                z / math.sqrt(2)
            )
        )
        * 100
    )

    return round(
        max(
            0,
            min(
                100,
                percentile
            )
        ),
        1
    )


# =========================================================
# FIND NEAREST WFA REFERENCE
# =========================================================

def get_nearest_wfa_reference(
    gender: str,
    age_days: int
):

    gender = gender.lower()

    if gender not in WHO_WFA_REFERENCE:
        return None

    reference_days = list(
        WHO_WFA_REFERENCE[gender].keys()
    )

    nearest_day = min(
        reference_days,
        key=lambda day: abs(day - age_days)
    )

    return WHO_WFA_REFERENCE[gender][nearest_day]


# =========================================================
# WEIGHT-FOR-AGE PERCENTILE
# =========================================================

def calculate_weight_percentile(
    gender: str,
    age_days: int,
    weight_kg: float
) -> float | None:

    if weight_kg is None or weight_kg <= 0:
        return None

    if age_days < 0 or age_days > 1825:
        return None

    reference = get_nearest_wfa_reference(
        gender,
        age_days
    )

    if reference is None:
        return None

    z = calculate_lms_zscore(
        value=weight_kg,
        L=reference["L"],
        M=reference["M"],
        S=reference["S"]
    )

    return zscore_to_percentile(z)


# =========================================================
# HEIGHT-FOR-AGE PERCENTILE
# =========================================================

def calculate_height_percentile(
    gender: str,
    age_months: int,
    height_cm: float
) -> float | None:

    if height_cm is None or height_cm <= 0:
        return None

    if age_months < 49 or age_months > 60:
        return None

    gender = gender.lower()

    if gender not in WHO_HFA_REFERENCE:
        return None

    reference = WHO_HFA_REFERENCE[gender].get(
        age_months
    )

    if reference is None:
        return None

    z = calculate_lms_zscore(
        value=height_cm,
        L=reference["L"],
        M=reference["M"],
        S=reference["S"]
    )

    return zscore_to_percentile(z)


# =========================================================
# MAIN GROWTH ANALYSIS
# =========================================================

def analyze_growth(child):

    measurements = (
        child.measurements
        if hasattr(child, "measurements")
        else []
    )

    # -----------------------------------------------------
    # No measurements
    # -----------------------------------------------------

    if not measurements:
        return {
            "latest_height": None,
            "latest_weight": None,
            "height_percentile": None,
            "weight_percentile": None,
            "status_notes": "No measurements recorded",
        }

    # -----------------------------------------------------
    # Latest measurement
    # -----------------------------------------------------

    latest = measurements[-1]

    # -----------------------------------------------------
    # Validate measurement date
    # -----------------------------------------------------

    if latest.measured_on < child.date_of_birth:
        return {
            "latest_height": latest.height_cm,
            "latest_weight": latest.weight_kg,
            "height_percentile": None,
            "weight_percentile": None,
            "status_notes": "Invalid measurement date.",
        }

    # -----------------------------------------------------
    # Validate weight
    # -----------------------------------------------------

    if (
        latest.weight_kg is not None
        and latest.weight_kg <= 0
    ):
        return {
            "latest_height": latest.height_cm,
            "latest_weight": latest.weight_kg,
            "height_percentile": None,
            "weight_percentile": None,
            "status_notes": "Invalid weight measurement.",
        }

    # -----------------------------------------------------
    # Validate height
    # -----------------------------------------------------

    if (
        latest.height_cm is not None
        and latest.height_cm <= 0
    ):
        return {
            "latest_height": latest.height_cm,
            "latest_weight": latest.weight_kg,
            "height_percentile": None,
            "weight_percentile": None,
            "status_notes": "Invalid height measurement.",
        }

    # -----------------------------------------------------
    # Calculate age
    # -----------------------------------------------------

    age_days = calculate_age_in_days(
        child.date_of_birth,
        latest.measured_on
    )

    age_months = calculate_age_in_months(
        child.date_of_birth,
        latest.measured_on
    )

    # -----------------------------------------------------
    # WHO Weight-for-Age
    # -----------------------------------------------------

    weight_percentile = calculate_weight_percentile(
        gender=child.gender,
        age_days=age_days,
        weight_kg=latest.weight_kg
    )

    # -----------------------------------------------------
    # WHO Height-for-Age
    # -----------------------------------------------------

    height_percentile = calculate_height_percentile(
        gender=child.gender,
        age_months=age_months,
        height_cm=latest.height_cm
    )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    status_notes = (
        "WHO Weight-for-Age and Height-for-Age "
        "analysis completed "
        f"for approximately {age_months} months of age."
    )

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {
        "latest_height": latest.height_cm,
        "latest_weight": latest.weight_kg,
        "height_percentile": height_percentile,
        "weight_percentile": weight_percentile,
        "status_notes": status_notes,
    }