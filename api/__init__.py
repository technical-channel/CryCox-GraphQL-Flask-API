import os
from flask import Flask, request, session, redirect
from flask_session import Session
from flask import Flask, request
from flask_cors import CORS
from ariadne import QueryType
from flask import Flask
from mongoengine import Document
from mongoengine.fields import StringField

import bson
import json
# from jsonpath import jsonpath
from mongoengine import connect
import os


try:
    db = "CrycoxDB"
    PASSWORD = "rahul"

    client = connect(
        db,
        host=f"mongodb+srv://rahul:{PASSWORD}@cluster0.4termek.mongodb.net/?retryWrites=true&w=majority",
        # host="mongodb://localhost:27017",
        alias="default",
    )
    print("connection successful")
except:
    print("not connecting")
# mongodb+srv://rahul:{PASSWORD}@cluster0.aojqm.mongodb.net/?retryWrites=true&w=majority
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'your secret key'
Session(app)
CORS(app)
query = QueryType()


@app.route('/')
def hello():
    return redirect("/graphql")
    # return """<p>Click on this button : </p>
    # <button class="graphql"
    # onclick="window.location.href = '/graphql';">
    #     graphql
    # </button>"""


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host="0.0.0.0", debug=True, port=8955)
