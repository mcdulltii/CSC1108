from flask_cors import CORS
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import pickle
import argparse
import os

import logging
from custom_logging import CustomFormatter

from routing.data_algo import RoutingAlgo

# Flask initializations
template_dir = os.path.abspath('static/')
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# argparse initializations
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Bus routes information')
parser.add_argument('-i', '--host', help='Hostname')
parser.add_argument('-p', '--port', help='Port number')
args = parser.parse_args()


@app.route('/')
def main():
    return render_template('index.html',
                           api_key=os.getenv('API_KEY'),
                           bus_selection=routes.keys() if routes is not None else None)


@app.route('/route/<bus_number>/<int:direction>')
def get_routes(bus_number, direction):
    key = f'{bus_number}_{direction}'
    if routes is None or key not in routes.keys():
        return invalid_page('Invalid bus route')
    return jsonify({key: [{'lat': i[1],'lng': i[0]} for i in routes[key]]})


@app.route('/route/get/<start>/<end>')
def get_shortest_route(start, end):
    routing = RoutingAlgo()
    try:
        return jsonify(routing.get_route(start, end))
    except:
        return invalid_page('Failed to get shortest route')


@app.route('/form-ori-dest', methods=["POST"])
def get_ori_dest():
    origin = request.form['origin']
    destination = request.form['destination']
    print(origin, destination)
    return 'Received origin and destination: {}, {}'.format(origin, destination)


@app.route('/marker_coord', methods=['POST'])
def get_marker_coord():
    data = request.get_json()
    lat = data['lat']
    lng = data['lng']
    print(lat, lng)
    return 'Received latitude and longitude of the marker'


@app.errorhandler(404)
def invalid_page(e):
    return jsonify({'errorCode': 404, 'message': str(e)})


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    load_dotenv()

    if args.file:
        with open(args.file, 'rb') as f:
            routes = pickle.load(f)
        logger.info(f'{routes.keys()=}')
    else:
        logger.warning('Load bus routes file for routes visualization feature')
        routes = None
    host = args.host if args.host else '127.0.0.1'
    port = int(args.port) if args.port else 8000
    app.run(host=host, port=port)
