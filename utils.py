import os
import uuid
from newspaper import Article
from ebooklib import epub

def fetch_article_as_epub(url):
    article = Article(url)
    article.download()
    article.parse()

    title = article.title.strip() if article.title else "無標題文章"
    content = article.text.strip() if article.text else "（⚠ 抱歉，這篇文章無法正確解析內容）"

    file_name = f"shellyread_{uuid.uuid4().hex}.epub"
    file_path = os.path.join("/tmp", file_name)

    book = epub.EpubBook()
    book.set_identifier(uuid.uuid4().hex)
    book.set_title(title)
    book.set_language("zh")

    chapter = epub.EpubHtml(title=title, file_name="chap.xhtml", lang="zh")
    chapter.content = f"<h1>{title}</h1><p>{content.replace(chr(10), '<br>')}</p>"

    book.add_item(chapter)
    book.spine = ['nav', chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(file_path, book)
    return file_path, title
