from flask import Flask
import os
from routes.main_routes import main_bp
from routes.chat_routes import chat_bp   # 🔥 ADD

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config["DATA_DIR"] = os.path.join(BASE_DIR, "data")

    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)   # 🔥 ADD

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
