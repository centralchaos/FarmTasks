from flask import Blueprint

installer = Blueprint('installer', __name__)

from app.installer import routes 