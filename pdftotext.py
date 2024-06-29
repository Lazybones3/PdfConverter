import sys, pathlib, pymupdf


def convert_pdf_to_text(pdf_file):
    doc = pymupdf.open(pdf_file)
    footer = "=============== Page %i of %i ================"
    text = ""
    for page in doc:
        page.insert_text(
            (50, page.rect.height - 50),
            footer % (page.number + 1, doc.page_count),
        )
        text += page.get_text()
        text += chr(12)
    # write as a binary file to support non-ASCII characters
    pathlib.Path(pdf_file.replace(".pdf", ".txt")).write_bytes(text.encode())
    doc.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: pdftotext <filename>")
        sys.exit()
    fname = sys.argv[1]
    convert_pdf_to_text(fname)
