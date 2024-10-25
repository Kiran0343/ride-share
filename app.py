import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)


app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<h1>Hello, World!</h1><p>Welcome to my dynamic website.</p>"

if __name__ == '__main__':
    app.run(debug=True)
