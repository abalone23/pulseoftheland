from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

POSTGRES = {
    'user': 'asilver',
    'pw': 'password',
    'db': 'rpdb',
    'host': 'localhost',
    'port': '5432',
}

app.config['SECRET_KEY'] = 'a1188a1c6f117c176afa1f6b38485ef5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://asilver@localhost/rpdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

from rpulse import routes