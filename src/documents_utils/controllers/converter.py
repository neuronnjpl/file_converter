import os
import argparse
from datetime import datetime

from documents_utils.models import pdf_reader, rules
from documents_utils.views import cli_view


def convert_file(pdf_path, output_dir, output_format, verbose, check_rules=False):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(pdf_output_dir, exist_ok=True)

    if verbose:
        cli_view.print_processing(os.path.basename(pdf_path))

    try:
        tables = pdf_reader.extract_tables(pdf_path)

        if verbose:
            cli_view.print_table_count(os.path.basename(pdf_path), tables.n)

        if tables.n == 0:
            cli_view.print_no_tables(os.path.basename(pdf_path))
            return False

        for i, table in enumerate(tables):
            filename = f"table_{i + 1}.{output_format}"
            output_path = os.path.join(pdf_output_dir, filename)

            if output_format == "csv":
                table.to_csv(output_path)
            elif output_format == "json":
                table.to_json(output_path)
            elif output_format == "excel":
                table.to_excel(output_path)

            if verbose:
                cli_view.print_table_saved(i + 1, output_path)

            if output_format == "csv" and check_rules:
                result = rules.check_regle_1(output_path)
                cli_view.print_rule_1_result(output_path, result)

        return True

    except Exception as e:
        cli_view.print_error(pdf_path, e)
        return False


def convert_directory(args):
    if args.check_rules and args.output_format != "csv":
        cli_view.print_check_rules_warning()
        args.check_rules = False

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join(args.output_dir, f"output_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    all_files = os.listdir(args.input_dir)
    pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
    non_pdf_count = len(all_files) - len(pdf_files)

    total = len(pdf_files)
    processed = 0
    with_tables = 0

    if args.verbose:
        cli_view.print_directory_header(output_dir, total, args.input_dir, non_pdf_count)

    for pdf_file in pdf_files:
        input_path = os.path.join(args.input_dir, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        pdf_output_dir = os.path.join(output_dir, base_name)

        if args.skip_existing and os.path.isdir(pdf_output_dir):
            if args.verbose:
                cli_view.print_skip(pdf_file)
            continue

        has_tables = convert_file(input_path, output_dir, args.output_format, args.verbose, args.check_rules)
        processed += 1
        if has_tables:
            with_tables += 1

    cli_view.print_summary(output_dir, total, processed, with_tables, non_pdf_count)


def main():
    parser = argparse.ArgumentParser(description="Extract tables from all PDFs in a directory using Camelot.")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files.")
    parser.add_argument("--output-dir", default=".", help="Directory to save the output.")
    parser.add_argument("--output-format", default="csv", choices=["csv", "json", "excel"], help="Output format.")
    parser.add_argument("--verbose", action="store_true", help="Print verbose information.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip PDFs already processed.")
    parser.add_argument("--check-rules", action="store_true", help="Activer la vérification des règles métiers après extraction.")

    args = parser.parse_args()
    convert_directory(args)
