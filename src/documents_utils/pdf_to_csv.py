import argparse
import os
import camelot
from datetime import datetime
import sys
import traceback

from documents_utils.rules import check_regle_1


def silent_unraisable_hook(unraisable):
    #  Pour eviter Les traceback inutiles a la fin du programme
    if isinstance(unraisable.exc_value, PermissionError):
        # Ignore les PermissionError lors de l'arrêt
        return
    # Sinon, on affiche normalement
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = silent_unraisable_hook

def convert_pdf_file(pdf_path, output_dir, output_format, verbose, check_rules=False):

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(pdf_output_dir, exist_ok=True)

    if verbose:
        print(f"\nProcessing file: {os.path.basename(pdf_path)}")

    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")

        if verbose:
            print(f"Found {tables.n} table(s) in {os.path.basename(pdf_path)}")

        if tables.n == 0:
            print(f"🤷 Aucun tableau trouvé dans {os.path.basename(pdf_path)}. Peut-être une image scannée ?")
            return False

        for i, table in enumerate(tables):
            filename = f"table_{i + 1}.{output_format}"
            output_path = os.path.join(pdf_output_dir, filename)

            if output_format == "csv":
                table.to_csv(output_path)
                if check_rules:
                    check_regle_1(output_path)
            elif output_format == "json":
                table.to_json(output_path)
            elif output_format == "excel":
                table.to_excel(output_path)

            if verbose:
                print(f"Saved table {i + 1} to {output_path}")

        return True

    except Exception as e:
        print(f"⚠️  Error processing {pdf_path}: {e}")
        return False



def convert_all_pdfs(args):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    temp_output_dir = os.path.join(args.output_dir, f"output_{timestamp}")
    os.makedirs(temp_output_dir, exist_ok=True)

    all_files = os.listdir(args.input_dir)
    pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
    non_pdf_files = len(all_files) - len(pdf_files)

    total_files = len(pdf_files)
    total_processed = 0
    total_with_tables = 0

    if args.verbose:
        print(f"\n🗂️  Résultats enregistrés dans : {temp_output_dir}")
        print(f"📦 {total_files} fichier(s) PDF trouvé(s) dans {args.input_dir}")
        if non_pdf_files > 0:
            print(f"🚫 {non_pdf_files} fichier(s) non-PDF ignoré(s)")


    for pdf_file in pdf_files:
        input_path = os.path.join(args.input_dir, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        pdf_output_dir = os.path.join(temp_output_dir, base_name)

        if args.skip_existing and os.path.isdir(pdf_output_dir):
            if args.verbose:
                print(f"Skipping already processed file: {pdf_file}")
            continue

        has_tables = convert_pdf_file(input_path, temp_output_dir, args.output_format, args.verbose, args.check_rules)
        total_processed += 1
        if has_tables:
            total_with_tables += 1

    print("\n✅ Extraction terminée.")
    print(f"📁 Dossier de sortie : {temp_output_dir}")
    print(f"📄 Fichiers PDF trouvés         : {total_files}")
    print(f"🔁 Fichiers effectivement traités : {total_processed}")
    print(f"✅ Fichiers avec tableau(x)      : {total_with_tables}")
    print(f"🚫 Fichiers non-PDF ignorés     : {non_pdf_files}")

    print("ℹ️ Si une erreur concernant les fichiers temporaires apparaît, elle peut être ignorée.")


def main():
    parser = argparse.ArgumentParser(description="Extract tables from all PDFs in a directory using Camelot.")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files.")
    parser.add_argument("--output-dir", default=".", help="Directory to save the output.")
    parser.add_argument("--output-format", default="csv", choices=["csv", "json", "excel"], help="Output format.")
    parser.add_argument("--verbose", action="store_true", help="Print verbose information.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip PDFs already processed.")
    parser.add_argument(
        "--check-rules",
        action="store_true",
        help="Activer la vérification des règles métiers après extraction des tables."
    )

    args = parser.parse_args()
    convert_all_pdfs(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if isinstance(e, PermissionError) and "Temp" in str(e):
            pass  # Ignore proprement les erreurs sur les fichiers temporaires
        else:
            traceback.print_exc()
            sys.exit(1)
