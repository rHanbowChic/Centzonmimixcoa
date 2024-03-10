from lugh_core import Lugh
from sys import argv, exit
from os import path, makedirs
import platformdirs
import signal


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

import re
import codecs

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)

def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)

def run_interactive_shell():
    signal.signal(signal.SIGINT, lambda x, y: exit(0))
    while True:
        print("> ", end="")
        command = input()
        c = command.split()

        if len(c) == 2:
            key = c[0]
            page = c[1]
            if page[-1] == ".":
                page = page[:-1]
                if n.post_note(key, page, "") == "":
                    print("Posted")
            else:
                print(n.get_note(key, page))
        elif len(c) == 3:
            key = c[0]
            page = c[1]
            text = decode_escapes(c[2])  # Replace escapes, like \n to real newline
            if n.post_note(key, page, text) == "":
                print("Posted")


n = Lugh(host=host, proxy=proxy)

if len(argv) < 3:
    print("Centzonmimixcoa v1.0 Interactive Shell")
    run_interactive_shell()
elif len(argv) == 3:
    key = argv[1]
    page = argv[2]
    if page[-1] == ".":
        page = page[:-1]
        print(n.post_note(key, page, ""))
    else:
        print(n.get_note(key, page))
elif len(argv) == 3:
    key = argv[1]
    page = argv[2]
    text = decode_escapes(argv[3])
    print(n.post_note(key, page, text))
