from flask import render_template
from web.picoweb import picoweb

@picoweb.route('/')
def index():
    return render_template('index.html')
