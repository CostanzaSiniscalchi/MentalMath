# Mental Math Application
from flask import Flask
from routes import register_routes
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
