# Convertisseur PDF vers CSV

Extrait les tableaux de fichiers PDF vectoriels et les exporte en CSV, JSON ou Excel.

> **Limitation** : fonctionne uniquement sur les PDFs vectoriels (avec bordures de tableau). Les PDFs scannés (images) ne sont pas supportés.

---

## Installation

**Prérequis** : Python 3.8+

```bash
# Créer et activer un environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## Utilisation

```bash
python bin/run_converter.py --input-dir <dossier_pdfs> --output-dir <dossier_sortie> [options]
```

### Options

| Option | Défaut | Description |
|--------|--------|-------------|
| `--input-dir` | *(requis)* | Dossier contenant les PDFs |
| `--output-dir` | `.` | Dossier de sortie |
| `--output-format` | `csv` | Format de sortie : `csv`, `json`, `excel` |
| `--verbose` | — | Affiche le détail du traitement |
| `--skip-existing` | — | Ignore les PDFs déjà traités |
| `--check-rules` | — | Vérifie les règles métier après extraction (CSV uniquement) |

Les fichiers sont enregistrés dans un sous-dossier horodaté :
`<output-dir>/output_YYYY-MM-DD_HH-MM-SS/<nom_pdf>/table_1.csv`

### Exemple

```bash
python bin/run_converter.py --input-dir assets/sample_base_first --output-dir tmp --output-format csv --verbose
```

```
🗂️  Résultats enregistrés dans : tmp\output_2025-04-04_16-22-52
📦 2 fichier(s) PDF trouvé(s) dans assets/sample_base_first
🚫 1 fichier(s) non-PDF ignoré(s)

Processing file: 111.pdf
Found 2 table(s) in 111.pdf
Saved table 1 to tmp\output_2025-04-04_16-22-52\111\table_1.csv
Saved table 2 to tmp\output_2025-04-04_16-22-52\111\table_2.csv

✅ Extraction terminée.
📁 Dossier de sortie : tmp\output_2025-04-04_16-22-52
📄 Fichiers PDF trouvés         : 2
🔁 Fichiers effectivement traités : 2
✅ Fichiers avec tableau(x)      : 2
🚫 Fichiers non-PDF ignorés     : 1
```

---

## Interface web (Streamlit)

L'interface permet d'analyser visuellement un répertoire : tri par catégorie, mise en évidence des violations, détail des tableaux extraits.

### Lancement en ligne de commande

```bash
.venv\Scripts\streamlit.exe run bin/app.py
```

L'application s'ouvre automatiquement sur **http://localhost:8501**.

### Lancement depuis PyCharm

**Run → Edit Configurations… → + → Python**

| Champ | Valeur |
|-------|--------|
| **Name** | `Streamlit app` |
| **Module name** | `streamlit` |
| **Parameters** | `run bin/app.py` |
| **Working directory** | racine du projet |
| **Python interpreter** | `.venv` |

> Utilise **Module name** (pas *Script path*) — bascule via le menu déroulant à gauche du champ.

Streamlit recharge l'app automatiquement à chaque sauvegarde de `app.py`.

---

## Règles métier (`--check-rules`)

Après extraction, le flag `--check-rules` applique des validations sur les données :

| Règle | Description |
|-------|-------------|
| **Règle 1** | Le montant *"total saisissable"* doit être strictement inférieur au *"solde bancaire insaisissable à retenir"* (seuil légal de minimum vital). |

---

## Tests

```bash
pytest tests/ -v
```

---

## Structure du projet

```
bin/
  run_converter.py          # Point d'entrée CLI
src/documents_utils/
  models/
    pdf_reader.py           # Extraction des tableaux (Camelot)
    rules.py                # Règles métier
  views/
    cli_view.py             # Affichage console
  controllers/
    converter.py            # Orchestration
assets/                     # PDFs d'exemple
tests/                      # Tests automatisés
```
