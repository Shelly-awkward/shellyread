# shellyread/app.py
from flask import Flask, request, render_template, redirect, url_for, flash
from utils import fetch_article_as_epub
from mailer import send_to_kindle
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "shellysecret")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash("請輸入網址", "error")
            return redirect(url_for('index'))

        try:
            epub_path, title = fetch_article_as_epub(url)
            send_to_kindle(epub_path, title)
            flash(f"✅ 成功將《{title}》寄送至 Kindle！", "success")
        except Exception as e:
            flash(f"❌ 發生錯誤：{str(e)}", "error")

        return redirect(url_for('index'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# shellyread/utils.py
import os
import uuid
from newspaper import Article
from ebooklib import epub

def fetch_article_as_epub(url):
    article = Article(url)
    article.download()
    article.parse()

    title = article.title or "Untitled"
    file_name = f"shellyread_{uuid.uuid4().hex}.epub"
    file_path = os.path.join("/tmp", file_name)

    book = epub.EpubBook()
    book.set_identifier(uuid.uuid4().hex)
    book.set_title(title)
    book.set_language("zh")

    chapter = epub.EpubHtml(title=title, file_name="chap.xhtml", lang="zh")
    chapter.content = f"<h1>{title}</h1>" + article.text.replace('\n', '<br>')

    book.add_item(chapter)
    book.spine = ['nav', chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(file_path, book)
    return file_path, title

# shellyread/mailer.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_to_kindle(file_path, title):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    kindle_email = os.getenv("KINDLE_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = kindle_email
    msg["Subject"] = "Convert"

    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_email, smtp_pass)
        server.sendmail(smtp_email, kindle_email, msg.as_string())

# templates/index.html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ShellyRead</title>
  <style>
    body {
      font-family: sans-serif;
      background: #fefefe;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
    }
    h1 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
    }
    input, button {
      font-size: 1rem;
      padding: 0.75rem;
      margin: 0.5rem 0;
      width: 90vw;
      max-width: 500px;
    }
    .message {
      margin-top: 1rem;
      color: green;
    }
  </style>
</head>
<body>
  <h1>📨 ShellyRead – 推送文章到 Kindle</h1>
  <form method="POST">
    <input type="text" name="url" placeholder="貼上文章網址..." required />
    <button type="submit">送出到 Kindle</button>
  </form>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="message">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
</body>
</html>

# .env.example
SMTP_EMAIL=youremail@gmail.com
SMTP_PASSWORD=your_app_password
KINDLE_EMAIL=yourkindle@kindle.com
FLASK_SECRET=random_secret_key

# requirements.txt
Flask
newspaper3k
ebooklib

# README.md
# ShellyRead – 一鍵將文章推送到 Kindle

## ✨ 功能
- 貼上網頁網址 → 自動抓取文章主文
- 轉成 EPUB 檔案 → 寄送到你的 Kindle
- 響應式網頁介面，手機電腦皆可用

## 🚀 使用方法
1. 建立 `.env` 檔案，填入 Gmail、密碼與 Kindle 信箱：
```
SMTP_EMAIL=dinefour@gmail.com
SMTP_PASSWORD=【你的 Gmail 應用程式密碼】
KINDLE_EMAIL=dinefour_scribe@kindle.com
FLASK_SECRET=隨便一串密碼
```

2. 安裝套件並啟動：
```
pip install -r requirements.txt
python app.py
```

3. 打開 http://localhost:5000，貼上網址，就會自動寄到 Kindle！

## 📦 部署建議：Railway、Render、Fly.io
- 支援 `.env` 自動管理
- 免費方案夠用

## 🙋‍♀️ 作者
ShellyRead 是為 dinefour 打造的個人化閱讀小幫手 ❤️
