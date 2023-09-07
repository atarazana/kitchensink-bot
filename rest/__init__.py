from flask import Flask

# Initialize the Flask web application
rest = Flask(__name__)

# Import your routes
from rest import rest_routes  # noqa
