import sys, os
from operator import itemgetter
from datetime import datetime

from flask import Flask, request, jsonify
from flask_api import status

import flask_sqlalchemy
import requests

from model import *

def generate_app():
    app = Flask(os.getenv('APP_NAME', __name__))

    app.config['DEBUG'] = os.getenv('DEBUG', False)

    app.config['SQLALCHEMY_ECHO'] = os.getenv('ECHO', False)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('TRACK', False)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URL']

    return app

def connect_to_db(app):
    db = flask_sqlalchemy.SQLAlchemy(app)

    @app.before_first_request
    def setup():
        sys.modules['model'].Base.metadata.create_all(bind=db.engine)

    return db

app = generate_app()
db = connect_to_db(app)

def save_navdata(event, timestamp):
    row = Navdata(event, timestamp)

    db.session.add(row)

@app.route('/', methods = ['POST'])
def post():
    body = request.get_json() if request.data != b'' else None

    if body.get('payload') == None:
        save_navdata(body['event'], body['timestamp'])
    else:
        for data in body['payload']:
            save_navdata(data['event'], data['timestamp'])

    db.session.commit()

    return jsonify(body), status.HTTP_201_CREATED

@app.route('/timeline', methods=['GET'])
def get_events():
    response = requests.get(os.getenv('ENDPOINT', 'https://storage.googleapis.com/dito-questions/events.json')).json()

    event_dict = get_built_dict_from_response(response)
    event_list = [event_dict[i] for i in list(event_dict)]

    timeline = {
        "timeline": sorted(event_list, key=lambda k: datetime.strptime(k['timestamp'][:26] + k['timestamp'][27:], '%Y-%m-%dT%H:%M:%S.%f%z'), reverse=True)
    }

    return jsonify(timeline)

def get_dict_from_arr(arr):
    obj = {}
    for row in arr:
        obj[row["key"]] = row["value"]

    return obj

def get_built_dict_from_response(response):
    events = {}

    for row in response["events"]:
        if row["event"] == "comprou-produto":
            row_data = get_dict_from_arr(row["custom_data"])
            rid = row_data["transaction_id"]

            if events.get(rid) == None: events[rid] = {}
            if events[rid].get("products") == None: events[rid]["products"] = []

            events[rid]["products"] += [{
                "name": row_data["product_name"],
                "price": row_data["product_price"]
            }]
        else:
            row_data = get_dict_from_arr(row["custom_data"])
            rid = row_data["transaction_id"]

            if events.get(rid) == None: events[rid] = {}

            events[rid]["timestamp"] = row["timestamp"]
            events[rid]["revenue"] = row["revenue"]
            events[rid]["transaction_id"] = rid
            events[rid]["store_name"] = row_data["store_name"]

    return events

@app.route('/complete/<search_query>/', methods = ['GET'])
def get_full_search(search_query):
    return get_navdata(search_query)

@app.route('/complete/<search_query>/suggestions', methods = ['GET'])
def get_suggestions_only(search_query):
    return get_navdata(search_query, True)

def get_navdata(search_query, suggestions_only=False):
    result = {}
    suggestions = None if len(search_query) < 2 else db.session.query(Navdata.event).filter(Navdata.event.ilike(f'{search_query}%')).distinct().all()

    if suggestions != None:
        result['suggestions'] = [j for i in suggestions for j in i]

    if (suggestions == None or len(suggestions)) and not suggestions_only:
        objects = db.session.query(Navdata).filter(Navdata.event == search_query).all()

        if len(objects): result['objects'] = [i.serialize for i in objects]

    return jsonify(result), status.HTTP_200_OK

if __name__ == '__main__':
    app.run(debug=True)
