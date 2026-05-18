import csv
import operator as op
from typing import Optional, NamedTuple

from documents_utils.models.rule_registry import RuleConfig

_OPS = {"<": op.lt, "<=": op.le, ">": op.gt, ">=": op.ge, "==": op.eq, "!=": op.ne}


class RuleResult(NamedTuple):
    rule_id: str
    rule_name: str
    ok: bool
    value_a: Optional[float]
    value_b: Optional[float]
    operator: str
    has_data: bool


class RegleResult(NamedTuple):
    """Legacy — conservé pour la compatibilité avec les tests."""
    ok: bool
    saisissable: Optional[float]
    insaisissable: Optional[float]


def _parse_amount(s) -> Optional[float]:
    try:
        return float(str(s).replace("EUR", "").replace(",", ".").strip())
    except Exception:
        return None


def check_rule(csv_file_path: str, rule: RuleConfig) -> RuleResult:
    value_a = None
    value_b = None

    with open(csv_file_path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            label = row[0].strip().lower()
            amount = _parse_amount(row[1])
            if amount is None:
                continue
            if rule.label_a in label:
                value_a = amount
            elif rule.label_b in label:
                value_b = amount

    has_data = value_a is not None and value_b is not None
    ok = _OPS.get(rule.operator, op.lt)(value_a, value_b) if has_data else False

    return RuleResult(
        rule_id=rule.id,
        rule_name=rule.name,
        ok=ok,
        value_a=value_a,
        value_b=value_b,
        operator=rule.operator,
        has_data=has_data,
    )


def check_regle_1(csv_file_path: str) -> RegleResult:
    """Legacy — conservé pour la compatibilité avec les tests."""
    rule = RuleConfig(
        id="regle_1", name="Règle 1", description="",
        enabled=True, label_a="total saisissable", label_b="insaisissable", operator="<",
    )
    r = check_rule(csv_file_path, rule)
    return RegleResult(ok=r.ok, saisissable=r.value_a, insaisissable=r.value_b)
