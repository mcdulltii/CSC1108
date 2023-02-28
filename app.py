from flask_cors import CORS
from flask import Flask, jsonify
import pickle
import argparse

# Flask initializations
app = Flask(__name__)
CORS(app)

# argparse initializations
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Bus routes information')
parser.add_argument('-i', '--host', help='Hostname')
parser.add_argument('-p', '--port', help='Port number')
args = parser.parse_args()


@app.route('/')
def main():
    return


if __name__ == '__main__':
    if args.file:
        with open(args.file, 'r') as f:
            routes = pickle.load(f)
    host = args.host if args.host else '127.0.0.1'
    port = int(args.port) if args.port else 80
    app.run(host=host, port=port)
