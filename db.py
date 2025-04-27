from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
