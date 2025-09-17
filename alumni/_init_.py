# alumni/__init__.py
from flask import Blueprint

alumni_bp = Blueprint("alumni", __name__)

from . import routes
