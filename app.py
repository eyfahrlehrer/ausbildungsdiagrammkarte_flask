from flask import Flask
from models import db
from main.routes import main  # Blueprint



app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)
