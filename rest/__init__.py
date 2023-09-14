from flask import Flask

# Initialize the Flask web application
rest = Flask(__name__, static_folder='build', static_url_path='/')

# Import your routes
from rest import rest_routes  # noqa
