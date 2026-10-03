"""
Rule-based nutrition plan generator.

Targets are reference values (US IOM Dietary Reference Intakes; energy values are
rough estimates). Every generated plan starts as `pending_review` -- a doctor must
approve it ("Clinical Validation: Review before feeding" in the UI).
"""

from datetime import date

from ..models import ChildProfile as Child, Gender, PregnancyProfile
from ..utils import age_in_months


# (max_age_months_exclusive, kcal, protein_g, iron_mg, calcium_mg)
_CHILD_DRI = [
    (6, 550, 9.1, 0.27, 200),
    (12, 750, 11, 11, 260),
    (48, 1000, 13, 7, 700),
    (108, 1400, 19, 10, 1000),
    (168, 1800, 34, 8, 1300),
]


ALLERGEN_SYNONYMS = {
    "peanut": ["peanut", "groundnut", "cheena badam", "nuts"],
    "tree_nut": ["almond", "cashew", "walnut", "pistachio", "tree nut", "nuts"],
    "milk": ["milk", "dairy", "lactose", "doodh"],
    "egg": ["egg", "dim"],
    "fish": ["fish", "maach"],
    "shellfish": ["shrimp", "prawn", "chingri", "crab", "shellfish"],
    "wheat": ["wheat", "gluten", "atta", "suji"],
    "soy": ["soy", "soya", "tofu"],
}


# name, slots, allergens, min_age_months, diet(veg|egg|nonveg)
FOODS = [
    (
        "Suji (semolina) porridge with milk",
        {"breakfast"},
        {"wheat", "milk"},
        6,
        "veg",
    ),
    (
        "Mashed banana",
        {"breakfast", "snack"},
        set(),
        6,
        "veg",
    ),
    (
        "Rice & lentil khichuri with vegetables",
        {"lunch", "dinner"},
        set(),
        6,
        "veg",
    ),
    (
        "Pumpkin, carrot & potato mash",
        {"lunch", "dinner"},
        set(),
        6,
        "veg",
    ),
    (
        "Seasonal fruit (papaya, mango, apple)",
        {"snack"},
        set(),
        6,
        "veg",
    ),
    (
        "Masoor dal with soft rice",
        {"lunch", "dinner"},
        set(),
        7,
        "veg",
    ),
    (
        "Yogurt (plain doi)",
        {"snack"},
        {"milk"},
        8,
        "veg",
    ),
    (
        "Boneless fish curry with rice",
        {"lunch", "dinner"},
        {"fish"},
        8,
        "nonveg",
    ),
    (
        "Chicken & vegetable soup",
        {"lunch", "dinner"},
        set(),
        8,
        "nonveg",
    ),
    (
        "Boiled egg",
        {"breakfast"},
        {"egg"},
        8,
        "egg",
    ),
    (
        "Egg & vegetable omelette",
        {"breakfast"},
        {"egg"},
        10,
        "egg",
    ),
    (
        "Soft roti with vegetable curry",
        {"dinner", "breakfast"},
        {"wheat"},
        10,
        "veg",
    ),
    (
        "Palong shak (spinach) with dal",
        {"lunch"},
        set(),
        10,
        "veg",
    ),
    (
        "Glass of milk",
        {"breakfast", "snack"},
        {"milk"},
        12,
        "veg",
    ),
    (
        "Chira with milk & banana",
        {"breakfast"},
        {"milk"},
        12,
        "veg",
    ),
    (
        "Peanut butter toast",
        {"breakfast", "snack"},
        {"peanut", "wheat"},
        12,
        "veg",
    ),
    (
        "Almond & date milkshake",
        {"snack"},
        {"tree_nut", "milk"},
        12,
        "veg",
    ),
    (
        "Tofu & vegetable stir-fry",
        {"lunch"},
        {"soy"},
        12,
        "veg",
    ),
    (
        "Shrimp curry with rice",
        {"lunch"},
        {"shellfish"},
        12,
        "nonveg",
    ),
    (
        "Chickpea (chola) salad",
        {"snack", "lunch"},
        set(),
        24,
        "veg",
    ),
    (
        "Grilled chicken with rice & salad",
        {"lunch", "dinner"},
        set(),
        24,
        "nonveg",
    ),
]


def match_allergens(
    allergies: list[str],
) -> tuple[set[str], list[str]]:
    """Return (allergen keys, unmatched allergy strings)."""

    keys, unmatched = set(), []

    for raw in allergies or []:
        text = raw.strip().lower()

        if not text or text in {"none", "no", "n/a"}:
            continue

        hit = {
            key
            for key, synonyms in ALLERGEN_SYNONYMS.items()
            if any(synonym in text for synonym in synonyms)
        }

        if hit:
            keys |= hit
        else:
            unmatched.append(raw)

    return keys, unmatched


def _diet_filter(habits: str | None):
    h = (habits or "").lower()

    if "vegan" in h:
        return (
            lambda f: f[4] == "veg" and not ({"milk", "egg"} & f[2]),
            False,
        )

    if "vegetarian" in h and "leaning" not in h:
        return (
            lambda f: f[4] != "nonveg",
            False,
        )

    return (
        lambda f: True,
        "leaning" in h,
    )


def _build_meals(
    slots,
    allergens,
    min_age_ok,
    habits,
    per_slot=2,
):
    allowed_by_diet, prefer_veg = _diet_filter(habits)

    removed, meals = set(), {}

    day_seed = date.today().toordinal()

    for slot in slots:
        options = []

        for food in FOODS:
            if (
                slot not in food[1]
                or not min_age_ok(food)
                or not allowed_by_diet(food)
            ):
                continue

            if food[2] & allergens:
                removed.add(food[0])
                continue

            options.append(food)

        options.sort(
            key=lambda f: (
                (f[4] != "veg") if prefer_veg else 0,
                f[0],
            )
        )

        if options:
            start = day_seed % len(options)
            rotated = options[start:] + options[:start]

            if prefer_veg:
                rotated = sorted(
                    rotated,
                    key=lambda f: f[4] != "veg",
                )

            meals[slot] = [
                food[0]
                for food in rotated[:per_slot]
            ]
        else:
            meals[slot] = []

    return meals, sorted(removed)


def plan_from_metrics(
    months: int,
    gender: Gender,
    allergies: list[str],
    habits: str | None,
    medical_conditions: str | None = None,
) -> dict:
    """
    Core calculator used by both saved child plans
    and the stateless /api/diet-plan endpoint.
    """

    notes, warnings = [], []

    # Make sure gender is handled as the Gender enum even if
    # the value comes from the database as a string.
    try:
        gender = Gender(gender)
    except (ValueError, TypeError):
        pass

    if months >= 168:
        female = gender == Gender.female

        kcal = 2000 if female else 2600
        protein = 46 if female else 52
        iron = 15 if female else 11
        calcium = 1300

    else:
        try:
            _, kcal, protein, iron, calcium = next(
                row for row in _CHILD_DRI
                if months < row[0]
            )
        except StopIteration:
            # Fallback for unexpected negative/invalid month values.
            _, kcal, protein, iron, calcium = _CHILD_DRI[0]

    targets = {
        "calories_kcal": kcal,
        "protein_g": protein,
        "iron_mg": iron,
        "calcium_mg": calcium,
    }

    allergens, unmatched = match_allergens(allergies)

    if months < 6:
        meals, removed = {}, []

        notes.append(
            "Under 6 months: exclusive breastfeeding "
            "(or infant formula) is recommended. "
            "No solid foods, water or honey."
        )

    else:
        slots = ["breakfast", "lunch", "dinner"]

        if months >= 12:
            slots.append("snack")

        meals, removed = _build_meals(
            slots,
            allergens,
            lambda f: f[3] <= months,
            habits,
        )

        if months < 12:
            notes.append(
                "Under 12 months: no honey, no cow's milk "
                "as a main drink, no added salt or sugar."
            )

        if months < 48:
            notes.append(
                "Avoid choking hazards: whole nuts, whole grapes, "
                "hard raw vegetables."
            )

    if allergens:
        warnings.append(
            "Allergy check: removed foods containing "
            + ", ".join(sorted(allergens)).replace("_", " ")
            + "."
        )

    for unmatched_allergy in unmatched:
        warnings.append(
            f"Allergy '{unmatched_allergy}' could not be matched "
            "to the food database - review manually."
        )

    if medical_conditions:
        warnings.append(
            "Medical conditions recorded - doctor review is required "
            "before following this plan."
        )

    notes.append(
        "Reference targets only. Review with a doctor before feeding."
    )

    return {
        "targets": targets,
        "meals": meals,
        "removed_foods": removed,
        "warnings": warnings,
        "notes": notes,
    }


def child_plan(child: Child) -> dict:
    """
    Plan for a saved child profile.
    Warnings are merged into notes for storage.
    """

    # age_in_months() returns the child's age in months.
    months = age_in_months(child.date_of_birth)

    r = plan_from_metrics(
        months=months,
        gender=child.gender,
        allergies=child.food_allergies,
        habits=child.dietary_habits,
        medical_conditions=child.medical_conditions,
    )

    return {
        "targets": r["targets"],
        "meals": r["meals"],
        "removed_foods": r["removed_foods"],
        "notes": r["warnings"] + r["notes"],
    }


def pregnancy_plan(p: PregnancyProfile) -> dict:
    tri = p.trimester

    extra_kcal = {
        1: 0,
        2: 340,
        3: 452,
    }[tri]

    targets = {
        "calories_kcal": 2000 + extra_kcal,
        "protein_g": 46 if tri == 1 else 71,
        "iron_mg": 27,
        "calcium_mg": 1000,
        "folate_mcg_dfe": 600,
        "trimester": tri,
        "week": p.week,
    }

    allergens, unmatched = match_allergens(
        p.food_allergies
    )

    meals, removed = _build_meals(
        ["breakfast", "lunch", "snack", "dinner"],
        allergens,
        lambda f: True,
        p.dietary_habits,
        per_slot=3,
    )

    notes = [
        "Avoid raw/undercooked eggs, meat and fish, "
        "unpasteurised milk, and high-mercury fish.",
        "Continue the iron-folic acid supplement prescribed "
        "by your doctor.",
    ]

    for unmatched_allergy in unmatched:
        notes.append(
            f"Allergy '{unmatched_allergy}' could not be matched "
            "to the food database - review manually."
        )

    if p.medical_conditions:
        notes.append(
            "Medical conditions recorded - doctor review is required "
            "before following this plan."
        )

    notes.append(
        "Reference targets only. Review with your doctor."
    )

    return {
        "targets": targets,
        "meals": meals,
        "removed_foods": removed,
        "notes": notes,
    }