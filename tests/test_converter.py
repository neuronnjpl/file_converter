import os
import pytest
import pandas as pd
from pathlib import Path

from documents_utils.pdf_to_csv import convert_pdf_file
from documents_utils.rules import check_regle_1


@pytest.fixture
def rtl_pdf():
    """PDF de test contenant un tableau valide pour test de règle."""
    #path = Path(os.getcwd()) / "assets" / "test1" / "tableau_exemple.pdf"
    path = Path(os.getcwd()) / "assets" / "test_avec_2_tableaux" / "111.pdf"
    if not path.is_file():
        raise FileNotFoundError(f"Le fichier de test est introuvable : {path}")
    return str(path)

@pytest.fixture
def output_dir(tmp_path):
    return tmp_path

def test_convert_pdf_file_with_rules(rtl_pdf, output_dir, capsys):
    result = convert_pdf_file(
        pdf_path=rtl_pdf,
        output_dir=str(output_dir),
        output_format="csv",
        verbose=False,
        check_rules=True
    )

    # Vérifie que le traitement s'est fait
    assert result is True, "Le fichier n'a pas été traité correctement."

    # Vérifie la présence d'au moins un CSV
    csv_files = list(output_dir.rglob("table_1.csv"))
    assert len(csv_files) >= 1, "Le fichier table_1.csv n’a pas été généré."

    csv_files = list(output_dir.rglob("table_2.csv"))
    assert len(csv_files) >= 1, "Le fichier table_1.csv n’a pas été généré."
    ok = check_regle_1(csv_files[0])
    assert not ok, "❌ La règle 1 a échoué pour table_2.csv"

    # Vérifie le contenu
    df = pd.read_csv(csv_files[0])
    assert df.shape[0] > 0, "Le fichier CSV généré est vide (lignes)."
    assert df.shape[1] > 0, "Le fichier CSV généré est vide (colonnes)."

    # Vérifie que la règle a bien été exécutée (grâce à l'affichage)
    captured = capsys.readouterr()
    assert "Vérification de la règle 1" in captured.out
