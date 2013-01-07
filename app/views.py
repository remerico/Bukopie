# coding: utf-8
from flask import render_template

from app import app, config

@app.route('/')
def index():
    return render_template('index.html', config=config)