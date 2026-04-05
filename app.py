#!/usr/bin/env python3
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return f"Hello World! Running on {os.uname().sysname}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
