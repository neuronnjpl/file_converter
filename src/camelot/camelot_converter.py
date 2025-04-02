import argparse
import os
import camelot

def main():
    parser = argparse.ArgumentParser(description="Extract tables from PDF using Camelot.")
    parser.add_argument("pdf_file", help="Path to the PDF file.")
    parser.add_argument("--output-dir", default=".", help="Directory to save the output.")
    parser.add_argument("--output-format", default="csv", choices=["csv", "json", "excel"], help="Output format.")
    parser.add_argument("--verbose", action="store_true", help="Print verbose information.")

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    if args.verbose:
        print(f"Reading PDF file: {args.pdf_file}")

    # Read tables from PDF (use lattice mode for bordered tables)
    tables = camelot.read_pdf(args.pdf_file, pages="all", flavor="lattice")

    if args.verbose:
        print(f"Found {tables.n} table(s)")

    for i, table in enumerate(tables):
        filename = f"table_{i + 1}.{args.output_format}"
        output_path = os.path.join(args.output_dir, filename)

        if args.output_format == "csv":
            table.to_csv(output_path)
        elif args.output_format == "json":
            table.to_json(output_path)
        elif args.output_format == "excel":
            table.to_excel(output_path)

        if args.verbose:
            print(f"Saved table {i + 1} to {output_path}")

if __name__ == "__main__":
    main()

