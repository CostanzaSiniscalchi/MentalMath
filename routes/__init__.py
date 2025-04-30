from .home_routes import home_bp
from .learn_routes import learn_bp
from .practice_routes import practice_bp
from .quiz_routes import quiz_bp

def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(learn_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(quiz_bp)
