import os
from flask import Flask, request, session, redirect, url_for
from app.config import config_by_name
from app.extensions import db, migrate


def create_app(config_name=None):
    """
    Flask Application Factory.
    Initializes Flask, loads configuration, registers extensions and blueprints.
    """
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder='infrastructure/templates',
        static_folder='infrastructure/static',
        static_url_path='/static'
    )

    # Load configuration object
    config_obj = config_by_name.get(config_name, config_by_name['development'])
    app.config.from_object(config_obj)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # type: ignore


    # Import domain models so Alembic can detect them
    with app.app_context():
        from app.domain import models  # noqa: F401
        
        # Create database tables automatically
        db.create_all()
        
        # Seed default admin user if database is empty
        from app.infrastructure.routes.auth import seed_default_user, seed_dummy_data
        seed_default_user()
        seed_dummy_data()
        
        # Initialize AWS/LocalStack resources (e.g. check and create S3 buckets)
        from app.infrastructure.aws import init_s3_bucket
        init_s3_bucket(app)

    # Register infrastructure blueprints
    from app.infrastructure.routes import main_bp
    from app.infrastructure.routes.auth import auth_bp
    from app.infrastructure.routes.kategori import kategori_bp
    from app.infrastructure.routes.barang import barang_bp
    from app.infrastructure.routes.ec2 import ec2_bp
    from app.infrastructure.routes.analytics import analytics_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(kategori_bp)
    app.register_blueprint(barang_bp)
    app.register_blueprint(ec2_bp)
    app.register_blueprint(analytics_bp)

    # Register context processor to make system status available to all templates
    @app.context_processor
    def inject_status():
        from app.application import StockService
        service = StockService()
        return dict(status=service.get_system_status())

    # Register Jinja template filter for S3 URLs
    @app.template_filter('s3_url')
    def get_s3_url(key):
        if not key:
            return None
        from app.application.services.storage import StorageService
        storage = StorageService()
        return storage.get_object_url(key)

    # Enforce authentication for all pages except static files and auth routes
    @app.before_request
    def require_login():
        if request.endpoint == 'static':
            return
        if request.endpoint in ['auth.login', 'auth.logout']:
            return
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

    return app
