import camelot


def extract_tables(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
    if tables.n == 0:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
    return tables
