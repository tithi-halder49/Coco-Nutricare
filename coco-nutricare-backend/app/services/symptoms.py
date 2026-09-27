"""Pregnancy danger-sign screening. Not a diagnosis - it only tells the mother to seek care now."""

DANGER_SIGNS = {
    "vaginal bleeding", "severe headache", "blurred vision", "severe abdominal pain", "fever",
    "swelling of face or hands", "reduced baby movement", "leaking fluid", "fits or convulsions",
    "difficulty breathing",
}
COMMON = ["nausea", "vomiting", "tiredness", "back pain", "heartburn", "constipation", "swollen feet"]
URGENT_MESSAGE = ("One or more of these can be a danger sign in pregnancy. "
                  "Contact your doctor or go to the nearest hospital now.")


def is_urgent(symptoms: list[str]) -> bool:
    return any(s.strip().lower() in DANGER_SIGNS for s in symptoms)
