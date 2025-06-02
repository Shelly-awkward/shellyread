from flask import Flask, request, render_template, redirect, url_for, flash
from utils import fetch_article_as_epub
from mailer import send_to_kindle
import os

print("🔧 Flask app is starting...")
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

print("🚀 Running app with debug=True, host='0.0.0.0'")
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
