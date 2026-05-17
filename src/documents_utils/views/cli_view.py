import os
from documents_utils.models.rules import RegleResult


def print_processing(filename):
    print(f"\nProcessing file: {filename}")


def print_table_count(filename, count):
    print(f"Found {count} table(s) in {filename}")


def print_no_tables(filename):
    print(f"🤷 Aucun tableau trouvé dans {filename}. Peut-être une image scannée ?")


def print_table_saved(index, path):
    print(f"Saved table {index} to {path}")


def print_skip(filename):
    print(f"Skipping already processed file: {filename}")


def print_directory_header(output_dir, total_files, input_dir, non_pdf):
    print(f"\n🗂️  Résultats enregistrés dans : {output_dir}")
    print(f"📦 {total_files} fichier(s) PDF trouvé(s) dans {input_dir}")
    if non_pdf > 0:
        print(f"🚫 {non_pdf} fichier(s) non-PDF ignoré(s)")


def print_summary(output_dir, total, processed, with_tables, non_pdf):
    print("\n✅ Extraction terminée.")
    print(f"📁 Dossier de sortie : {output_dir}")
    print(f"📄 Fichiers PDF trouvés         : {total}")
    print(f"🔁 Fichiers effectivement traités : {processed}")
    print(f"✅ Fichiers avec tableau(x)      : {with_tables}")
    print(f"🚫 Fichiers non-PDF ignorés     : {non_pdf}")
    print("ℹ️ Si une erreur concernant les fichiers temporaires apparaît, elle peut être ignorée.")


def print_rule_1_result(csv_path, result: RegleResult):
    filename = os.path.basename(csv_path)
    print(f"   🔍 Règle 1 — {filename}")
    if result.saisissable is None or result.insaisissable is None:
        print(f"      ℹ️  Non applicable (ce tableau ne contient pas de données de saisie)")
        return
    sai = result.saisissable
    ins = result.insaisissable
    print(f"      Saisissable : {sai:.2f} EUR  |  Insaisissable : {ins:.2f} EUR")
    if result.ok:
        print(f"      ✅ Conforme : {sai:.2f} < {ins:.2f}")
    elif sai == ins:
        print(f"      ❌ Violation : montants égaux ({sai:.2f} EUR) — le saisissable doit être strictement inférieur")
    else:
        print(f"      ❌ Violation : saisissable ({sai:.2f} EUR) dépasse l'insaisissable ({ins:.2f} EUR)")


def print_check_rules_warning():
    print("⚠️  --check-rules n'est disponible qu'avec --output-format csv, ignoré.")


def print_error(pdf_path, error):
    print(f"⚠️  Error processing {pdf_path}: {error}")
