import sys
import os
import pymupdf
from ebooklib import epub


def convert_pdf_to_epub(filename):
    # Read from Pdf
    doc = pymupdf.open(filename)
    # Write to Epub
    book = epub.EpubBook()
    # set metadata
    book.set_language("en")
    title = doc.metadata["title"]
    if title is None or title == '':
        title, _ = os.path.splitext(os.path.basename(filename))
    book.set_title(title)
    author = doc.metadata["author"]
    book.add_author(author)
    # basic spine
    book.spine = ['nav']
    for i, page in enumerate(doc.pages()):
        page_id = f"page_{i + 1}"
        file_name = f"{page_id}.xhtml"
        page_html = epub.EpubHtml(uid=page_id, title=page_id, file_name=file_name, lang="en")
        page_html.content = page.get_text("xhtml")
        # add chapter
        book.add_item(page_html)
        book.spine.append(page_id)
    # define Table Of Contents
    # [lvl, title, page]
    for toc in doc.get_toc():
        page_id = f"page_{toc[2]}"
        file_name = f"{page_id}.xhtml"
        book.toc.append(epub.Link(file_name, toc[1], page_id))
    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    # write to the file
    output_file = filename.replace(".pdf", ".epub")
    epub.write_epub(output_file, book)
    doc.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: pdftoepub <filename>")
        sys.exit()
    filename = sys.argv[1]
    convert_pdf_to_epub(filename)
