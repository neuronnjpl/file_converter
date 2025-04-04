import argparse
import sys
import traceback

sys.path.append("../src")
from documents_utils.pdf_to_csv import convert_all_pdfs


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