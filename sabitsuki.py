# 从Illusion以来我一直没能给任何一个项目自己想要的名字。现在不会了！
from os import path, makedirs
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import Response
from flaskext.markdown import Markdown
from bs4 import BeautifulSoup
from lugh_core import Lugh
import platformdirs
import random  # 最好的模块
import string
import sys

base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = path.join(sys._MEIPASS)

config_path = platformdirs.user_data_dir("ntms","ect.fyi")
if not path.exists(config_path):
    makedirs(config_path)

host_config_file_path = path.join(config_path, "ntms-host.cfg")
if path.isfile(host_config_file_path):
    with open(host_config_file_path, "r", encoding="utf-8") as f:
        host = f.read()
else:
    with open(host_config_file_path, "w+", encoding="utf-8") as f:
        f.write("https://note.ms/")
        host = "https://note.ms/"

proxy_config_file_path = path.join(config_path, "ntms-proxy.cfg")
if path.isfile(proxy_config_file_path):
    with open(proxy_config_file_path, "r", encoding="utf-8") as f:
        proxy = f.read()
else:
    with open(proxy_config_file_path, "w+", encoding="utf-8") as f:
        f.write("")
        proxy = ""

l = Lugh(host=host, proxy=proxy)

app = Flask("Sabitsuki", static_folder=path.join(base_dir, 'static'),
        template_folder=path.join(base_dir, 'templates'))
Markdown(app)

VALID_TAGS = ['strong', 'em', 'p', 'ul', 'ol', 'li', 'b', 'i',
              'br', 'sub', 'sup', 'ruby', 'rt', 'rp', 'details', 'summary']


# 通过去除除VALID_TAGS外所有的标签与VALID_TAGS标签的所有属性来避免XSS攻击。
def sanitize_html(text):
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup.findAll(True):
        if tag.name in VALID_TAGS:
            lst = []
            for attr in tag.attrs:
                lst.append(attr)
            for attr in lst:
                del tag[attr]
        else:
            tag.hidden = True

    return soup.renderContents().decode('utf-8')


@app.route("/<key>/<page>", methods=['GET'])
def page_get(key, page):
    if page.endswith(".md"):  # /example1.md
        page = page[0:-3]  # example1
        text = l.get_note(key, page)
        # 过滤可能的XSS
        text = sanitize_html(text)

        if (request.headers.get("User-Agent") is not None and (
                "curl/" in request.headers.get("User-Agent")
                or "Wget/" in request.headers.get("User-Agent")
        )):
            return Response(text, mimetype='text/plain')
        else:
            return render_template('note_md.html', key=key, page=page, text=text)
    else:
        text = l.get_note(key, page)

        is_text_request = request.args.get('text') is not None
        if (request.headers.get("User-Agent") is not None and (
                "curl/" in request.headers.get("User-Agent")
                or "Wget/" in request.headers.get("User-Agent")
                or is_text_request
        )):  # 给curl,Wget或带有text参数(?text)的请求直接显示内容
            return Response(text, mimetype='text/plain')
        else:
            return render_template('note.html', key=key, page=page, text=text)

@app.route("/<key>/<page>", methods=['POST'])
def note_post(key, page):
    if not page.endswith(".md"):
        t = request.form.get("t")
        if t is not None:
            l.post_note(key, page, t)
    return ""

@app.route("/<key>", methods=['GET'])
def root_redirect(key):
    selector_mode = request.args.get('selector') is not None
    if selector_mode:
        return render_template('page_selector.html', key=key)
    randword = ""
    for i in range(0, 4):
        randword += random.choice(string.ascii_lowercase)
    return redirect(f"/{key}/{randword}", code=302)


@app.route("/", methods=['GET'])
def show_welcome():
    return render_template('welcome.html')


@app.errorhandler(500)
def error_500(error):
    return "500 Error. <a href='/'>Return to main page</a>"


if __name__ == "__main__":
    app.run(port=5100)