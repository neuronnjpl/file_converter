import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "rules_config.json"

OPERATORS = ["<", "<=", ">", ">=", "==", "!="]

_DEFAULTS = [
    {
        "id": "regle_1",
        "name": "Règle 1",
        "description": "Total saisissable doit être strictement inférieur au solde bancaire insaisissable",
        "enabled": True,
        "label_a": "total saisissable",
        "label_b": "insaisissable",
        "operator": "<",
    }
]


@dataclass
class RuleConfig:
    id: str
    name: str
    description: str
    enabled: bool
    label_a: str
    label_b: str
    operator: str


class RuleRegistry:
    def __init__(self, config_path: Path = _CONFIG_PATH):
        self._path = Path(config_path)
        self._rules: List[RuleConfig] = []
        self._load()

    def _load(self):
        if self._path.exists():
            data = json.loads(self._path.read_text(encoding="utf-8"))
        else:
            data = _DEFAULTS
            self._save_data(data)
        self._rules = [RuleConfig(**r) for r in data]

    def _save_data(self, data):
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _save(self):
        self._save_data([asdict(r) for r in self._rules])

    @property
    def all(self) -> List[RuleConfig]:
        return list(self._rules)

    @property
    def enabled(self) -> List[RuleConfig]:
        return [r for r in self._rules if r.enabled]

    def add(self, name: str, description: str, label_a: str, label_b: str, operator: str) -> RuleConfig:
        rule = RuleConfig(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            enabled=True,
            label_a=label_a.strip().lower(),
            label_b=label_b.strip().lower(),
            operator=operator,
        )
        self._rules.append(rule)
        self._save()
        return rule

    def remove(self, rule_id: str):
        self._rules = [r for r in self._rules if r.id != rule_id]
        self._save()

    def set_enabled(self, rule_id: str, enabled: bool):
        for r in self._rules:
            if r.id == rule_id:
                r.enabled = enabled
        self._save()
