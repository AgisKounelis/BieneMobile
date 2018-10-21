from flask import Flask, request, jsonify
from src import super
app = Flask(__name__)


@app.route("/")
def hello():
    return "Goodpye!"


@app.route('/city/<city_name>', methods=['GET'])
def city(city_name):
    bus_count = request.args.get('busCount')
    total_distance = request.args.get('totalDistance')
    print("New request for " + bus_count + " buses with a total allowable distance of " + total_distance + " km")
    jsonify(super.Response(city_name = city_name, bus_count = bus_count, total_distance = total_distance))


if __name__ == "__main__":
    app.run()
