import sys
import os
import pymupdf
from ebooklib import epub
from typing import List


class PdfChapter:
    def __init__(self, id: int, title: str, content: str, page: int) -> None:
        self.id = id
        self.title = title
        self.content = content
        self.page = page


class PdfDocument:
    def __init__(self, title: str, author: str, chapter: List = []) -> None:
        self.title = title
        self.author = author
        self.chapters = chapter


class PdfConverter:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.pdf_doc = None

    def read_pdf(self) -> PdfDocument:
        doc = pymupdf.open(self.filename)
        toc = doc.get_toc()
        chapter_list = []
        # [lvl, title, page]
        for i in range(len(toc) - 1):
            _, title, cur_page = toc[i]
            _, _, next_page = toc[i + 1]
            content = ''
            if cur_page == next_page:
                continue
            for page in doc.pages(cur_page-1, next_page-1):
                content += page.get_text("xhtml")
            chapter = PdfChapter(i+1, title, content, cur_page)
            chapter_list.append(chapter)
        title = doc.metadata["title"]
        author = doc.metadata["author"]
        if title is None or title == '':
            title, _ = os.path.splitext(os.path.basename(self.filename))
        self.pdf_doc = PdfDocument(title, author, chapter_list)


    def write_epub(self) -> None:
        book = epub.EpubBook()
        document = self.pdf_doc

        # set metadata
        book.set_title(document.title)
        book.set_language("en")

        book.add_author(document.author)

        # basic spine
        book.spine = ['nav']

        # create chapter
        for c in document.chapters:
            chapter_id = f"chap_{c.id}"
            file_name = f"{chapter_id}.xhtml"
            chapter = epub.EpubHtml(uid=chapter_id, title=c.title, file_name=file_name, lang="en")
            chapter.content = c.content

            # add chapter
            book.add_item(chapter)

            # define Table Of Contents
            book.toc.append(epub.Link(file_name, c.title, chapter_id))

            book.spine.append(chapter_id)

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # write to the file
        output_file = self.filename.replace(".pdf", ".epub")
        epub.write_epub(output_file, book)

    def pdf_to_epub(self):
        self.read_pdf()
        self.write_epub()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: pdftoepub <filename>")
        sys.exit()
    filename = sys.argv[1]
    converter = PdfConverter(filename)
    converter.pdf_to_epub()
