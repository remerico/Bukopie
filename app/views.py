# coding: utf-8
from flask import render_template, request, send_from_directory, url_for

from app import app, config
from actions import handle_action

@app.route('/')
def index():
	return render_template('index.html', config=config)

@app.route('/action', methods=['POST'])
def action():
	if request.method == 'POST':
		handle_action(request.form['message'])
		return 'ready'
	else:
		return ''