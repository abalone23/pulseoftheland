from flask import Flask
from urllib.parse import quote_plus

app = Flask(__name__, static_url_path='', instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.jinja_env.filters['quote_plus'] = lambda u: quote_plus(u)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

from rpulse import routes