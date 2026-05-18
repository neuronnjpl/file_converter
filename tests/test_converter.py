import pytest
import pandas as pd
from pathlib import Path

from documents_utils.controllers.converter import convert_file
from documents_utils.models.rules import check_regle_1
from documents_utils.models.rule_registry import RuleConfig

ASSETS = Path(__file__).parent / "assets"
PDF_TWO_TABLES = ASSETS / "test_avec_2_tableaux" / "111.pdf"


# ---------------------------------------------------------------------------
# check_regle_1 — tests unitaires sur CSV synthétiques (rapides, sans PDF)
# ---------------------------------------------------------------------------

def test_regle_1_ok_quand_saisissable_inferieur(tmp_path):
    csv_path = tmp_path / "ok.csv"
    csv_path.write_text(
        "total saisissable,0.50 EUR\n"
        "solde bancaire insaisissable à retenir,1.00 EUR\n",
        encoding="utf-8",
    )
    assert check_regle_1(str(csv_path)).ok is True


def test_regle_1_violee_quand_saisissable_superieur(tmp_path):
    csv_path = tmp_path / "violated.csv"
    csv_path.write_text(
        "total saisissable,2.00 EUR\n"
        "solde bancaire insaisissable à retenir,1.00 EUR\n",
        encoding="utf-8",
    )
    assert check_regle_1(str(csv_path)).ok is False


def test_regle_1_donnees_insuffisantes_retourne_false(tmp_path):
    csv_path = tmp_path / "incomplete.csv"
    csv_path.write_text("autre label,1.00 EUR\n", encoding="utf-8")
    assert check_regle_1(str(csv_path)).ok is False


def test_regle_1_egalite_retourne_false(tmp_path):
    csv_path = tmp_path / "equal.csv"
    csv_path.write_text(
        "total saisissable,1.00 EUR\n"
        "solde bancaire insaisissable à retenir,1.00 EUR\n",
        encoding="utf-8",
    )
    assert check_regle_1(str(csv_path)).ok is False


# ---------------------------------------------------------------------------
# convert_file — tests d'intégration
# ---------------------------------------------------------------------------

def test_convert_retourne_true_et_cree_csv(tmp_path):
    result = convert_file(
        pdf_path=str(PDF_TWO_TABLES),
        output_dir=str(tmp_path),
        output_format="csv",
        verbose=False,
    )
    assert result is True
    assert len(list(tmp_path.rglob("*.csv"))) >= 1


def test_convert_deux_tableaux_cree_deux_fichiers(tmp_path):
    convert_file(
        pdf_path=str(PDF_TWO_TABLES),
        output_dir=str(tmp_path),
        output_format="csv",
        verbose=False,
    )
    assert len(list(tmp_path.rglob("table_1.csv"))) == 1
    assert len(list(tmp_path.rglob("table_2.csv"))) == 1


def test_convert_csv_non_vide(tmp_path):
    convert_file(
        pdf_path=str(PDF_TWO_TABLES),
        output_dir=str(tmp_path),
        output_format="csv",
        verbose=False,
    )
    csv_file = list(tmp_path.rglob("table_1.csv"))[0]
    df = pd.read_csv(csv_file)
    assert df.shape[0] > 0
    assert df.shape[1] > 0


def test_convert_fichier_inexistant_retourne_false(tmp_path):
    result = convert_file(
        pdf_path=str(tmp_path / "inexistant.pdf"),
        output_dir=str(tmp_path),
        output_format="csv",
        verbose=False,
    )
    assert result is False


def test_convert_avec_regles_affiche_verification(tmp_path, capsys):
    rule = RuleConfig(
        id="regle_1", name="Règle 1", description="",
        enabled=True, label_a="total saisissable", label_b="insaisissable", operator="<",
    )
    convert_file(
        pdf_path=str(PDF_TWO_TABLES),
        output_dir=str(tmp_path),
        output_format="csv",
        verbose=False,
        active_rules=[rule],
    )
    captured = capsys.readouterr()
    assert "Règle 1" in captured.out


def test_convert_avec_regles_detecte_violation_table_2(tmp_path):
    convert_file(
        pdf_path=str(PDF_TWO_TABLES),
        output_dir=str(tmp_path),
        output_format="csv",
        verbose=False,
    )
    table_2 = list(tmp_path.rglob("table_2.csv"))[0]
    assert check_regle_1(str(table_2)).ok is False
