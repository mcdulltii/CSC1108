from flask_cors import CORS
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import pickle
import argparse
import time
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
                           bus_selection=routes.keys() if routes is not None
                           else ['P101_1', 'P102_1', 'P102_2', 'P106_1', 'P202_1', 'P211_1', 'P211_2', 'P411_1', 'P411_2', 'P403_1'])


@app.route('/route/<bus_number>/<int:direction>')
def get_routes(bus_number, direction):
    # Get bus routes
    key = f'{bus_number}_{direction}'
    if routes is None or key not in routes.keys():
        return invalid_page('Invalid bus route')
    return jsonify({key: [{'lat': i[1], 'lng': i[0]} for i in routes[key]]})


@app.route('/form-ori-dest', methods=["POST"])
def get_ori_dest():
    # Calculate walking and bus route from origin to destination
    routing = RoutingAlgo()
    origin = request.form['origin']
    destination = request.form['destination']
    logger.info(f'{origin=}, {destination=}')
    try:
        start = time.time()
        route = routing.get_route(origin, destination)
        end = time.time()
        logging.info(f"Route retrieved in {end - start} seconds")
        return jsonify(route)
    except:
        return invalid_page('Failed to get shortest route')


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
