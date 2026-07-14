from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Centralized extension instances.
# Initialized here without an app context, then bound to the app in create_app().
db = SQLAlchemy()
migrate = Migrate()
