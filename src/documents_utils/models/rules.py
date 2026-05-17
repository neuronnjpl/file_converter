import csv
from typing import NamedTuple, Optional


class RegleResult(NamedTuple):
    ok: bool
    saisissable: Optional[float]
    insaisissable: Optional[float]


def _parse_amount(amount_str) -> Optional[float]:
    try:
        return float(amount_str.replace("EUR", "").replace(",", ".").strip())
    except Exception:
        return None


def check_regle_1(csv_file_path) -> RegleResult:
    """
    Règle 1 : "Total saisissable" doit être strictement inférieur à
    "Solde bancaire insaisissable à retenir" (minimum vital légal).
    """
    montant_saisissable = None
    montant_insaisissable = None

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        for row in csv.reader(csvfile):
            if len(row) < 2:
                continue
            label = row[0].strip().lower()
            montant = _parse_amount(row[1])
            if montant is None:
                continue
            if "total saisissable" in label:
                montant_saisissable = montant
            elif "insaisissable" in label:
                montant_insaisissable = montant

    if montant_saisissable is not None and montant_insaisissable is not None:
        ok = montant_saisissable < montant_insaisissable
    else:
        ok = False

    return RegleResult(ok=ok, saisissable=montant_saisissable, insaisissable=montant_insaisissable)