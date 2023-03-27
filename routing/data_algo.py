import os
import sys
import time
import pickle
from typing import List, Dict, Any

import googlemaps
import pprint as pp
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime

sys.path.append('../CSC1108')
from routes_reader.routes_reader import RoutesReader
from routing.dijkstras import Dijkstras
from routing.shortest_walk import shortest_walk
from collections import deque


class RoutingAlgo:
    # Variable declarations
    gmaps = None
    busstops = None
    mapBoxScrap = None
    routes_reader = None
    routeCalculator = None
    walkingRouteCalculator = None
    graphedData = {}
    parsedData = {}

    def __init__(self) -> None:
        # Initialize RoutesReader class
        self.routes_reader = RoutesReader()
        # Read bus stops from excel
        self.busstops = self.routes_reader.read_excel('bus_stops.xlsx')
        # Initialize Google maps API
        self.gmaps = googlemaps.Client("AIzaSyAB_QsjZviwHVJHyBCeTPiK8M1NOvSLcns")
        # Load bus routes from file
        dirpath = os.path.dirname(os.path.realpath(__file__))
        routes_path = os.path.join(dirpath, "../web_scraper/routes.bin")
        with open(routes_path, 'rb') as f:
            self.mapBoxScrap = pickle.load(f)
        self._load_bus_stops()
        self.walkingRouteCalculator = shortest_walk(self.parsedData)

        self._populate_routes_information()
        self.routeCalculator = Dijkstras(self.graphedData)

    def get_route(self, startingLocation: str, endingLocation: str) -> list[dict[str, list[Any] | Any]]:
        '''
        {
            Starting Bus Stop: startBusStop,
            Ending Bus Stop: endBusStop,
            Buses To Take: listOfBusesToTake, if there is more than 1 means there's a transfer,
            Route Taken: {Bus number: [list of routes...], Bus number 2: [list of routes....],
            Distance Travelled (KM) : distance travelled
        }
        '''
        # GET COORDINATES FROM STRING
        startingLocationCoords = self.walkingRouteCalculator.string_to_coordinate(startingLocation)
        endingLocationCoords = self.walkingRouteCalculator.string_to_coordinate(endingLocation)
        toReturn = {
            "Routes": []
        }

        # print(endingLocationCoords)

        startingCloseBusStop = self.walkingRouteCalculator.find_nearby(startingLocationCoords)
        startingBusStop = startingCloseBusStop[1]["Name"]
        # print(startingBusStop)

        endingCloseBusStop = self.walkingRouteCalculator.find_nearby(endingLocationCoords)
        endingBusStop = endingCloseBusStop[1]["Name"]
        # print(endingBusStop)
        if self._calculate_relative_distance(startingLocationCoords, startingBusStop["GPS Location"] > 0.05):
            toReturn["Routes"].append(
                {
                    "Route":startingCloseBusStop[0],
                    "Type": "Walking",
                    "Start": startingLocation,
                    "End": startingBusStop
                }
            )

        routeObject = self.routeCalculator.calculate_route(startingBusStop, endingBusStop)

        # print("Walking Route to " + startingBusStop + ":" + str(startingCloseBusStop[0]))

        startRecording = False
        busStopStart = routeObject["Pathing"][0]
        transfers = deque()
        for transfer in routeObject["Transfers"]:
            transfers.append(transfer)
        for busesToTake in routeObject["Buses To Return"]:
            toReturn["Routes"].append({
                "Type": busesToTake[0],
                "Route": []
            })
            transferObject = None
            if len(transfers) != 0:
                transferObject = transfers.popleft()
            indexOfBusStopStart = next(
                (index for (index, d) in enumerate(self.parsedData[busesToTake[0]]) if d["Name"] == busStopStart), None)
            busPointToCheck = self.parsedData[busesToTake[0]][indexOfBusStopStart]["Closest Point"]
            # print(self.parsedData[busesToTake[0]][indexOfBusStopStart])
            if transferObject is not None:
                if transferObject["Type"] == "Walking":
                    busStopEnd = transferObject["Transfer Stop From"]
                elif transferObject["Type"] == "On-Site":
                    busStopEnd = transferObject["Transfer Stop"]
            else:
                busStopEnd = routeObject["Pathing"][-1]
            indexOfBusStopEnd = next(
                (index for (index, d) in enumerate(self.parsedData[busesToTake[0]]) if d["Name"] == busStopEnd), None)
            busPointEnd = self.parsedData[busesToTake[0]][indexOfBusStopEnd]["Closest Point"]
            indexOf = list(self.parsedData.keys()).index(busesToTake[0])
            correspondingMapBoxKey = list(self.mapBoxScrap.keys())[indexOf]
            pointIterator = 0
            indexOfRouteObj = next(
                (index for (index, d) in enumerate(toReturn["Routes"]) if d["Type"] == busesToTake[0]), None)
            toReturn["Routes"][indexOfRouteObj]["Starting"] = busStopStart
            toReturn["Routes"][indexOfRouteObj]["Ending"] = busStopEnd
            startRecording = False
            while True:
                point = self.mapBoxScrap[correspondingMapBoxKey][pointIterator]
                if point == busPointToCheck:
                    # print("MATCH")
                    startRecording = True
                if startRecording:
                    toReturn["Routes"][indexOfRouteObj]["Route"].append(point)
                if point == busPointEnd and startRecording:
                    if transferObject is not None:
                        if transferObject["Type"] == "Walking":
                            busStopStart = transferObject["Transfer Stop To"]
                            nextBus = routeObject["Buses To Return"][
                                routeObject["Buses To Return"].index(busesToTake) + 1]

                            indexOfBusStopWalkingEnd = next(
                                (index for (index, d) in enumerate(self.parsedData[nextBus[0]]) if
                                 d["Name"] == busStopStart), None)
                            indexOfBusStopWalkingStart = next(
                                (index for (index, d) in enumerate(self.parsedData[busesToTake[0]]) if
                                 d["Name"] == transferObject["Transfer Stop From"]), None)
                            coordinatesEnd = self.parsedData[busesToTake[0]][indexOfBusStopWalkingEnd]["GPS Location"]
                            coordinatesStart = self.parsedData[nextBus[0]][indexOfBusStopWalkingStart]["GPS Location"]
                            toReturn["Routes"].append({
                                "Route": self.walkingRouteCalculator.get_walking_route(coordinatesStart,
                                                                                       coordinatesEnd),
                                "Type": "Walking",
                                "Start": transferObject["Transfer Stop From"],
                                "End": busStopStart
                            })
                        else:
                            busStopStart = transferObject["Transfer Stop"]
                    break
                pointIterator += 1
                # print(pointIterator)
                if pointIterator == len(self.mapBoxScrap[correspondingMapBoxKey]):
                    # print("reset")
                    pointIterator = 0
        if self._calculate_relative_distance(endingLocation,
                                             endingBusStop["GPS Location"] > 0.05):
            toReturn["Routes"].append(
                {
                    "Route": endingBusStop[0],
                    "Type": "Walking",
                    "Start": endingBusStop[1]["Name"],
                    "End": endingLocation
                }
            )
        returnRoutes = [toReturn]
        # print(toReturn)
        return returnRoutes

    def _load_bus_stops(self) -> None:
        # Iterate bus stops
        for i in range(0, len(self.busstops)):
            # Initialize bus stop in parsedData dictionary
            self.parsedData[list(self.busstops.keys())[i]] = []
            # Append bus stops with GPS coordinates
            for l, stop in self.busstops[list(self.busstops.keys())[i]].iterrows():
                self.parsedData[list(self.busstops.keys())[i]].append(
                    {
                        "Name": stop["Bus stop"],
                        "GPS Location": stop["GPS Location"]
                    }
                )
                self.graphedData[stop["Bus stop"]] = []

            key = list(self.parsedData.keys())[i]

            # Find the nearest point in bus route from bus stop coordinate
            self._find_nearest_points(i, key)

            # Calculate distance 
            busServiceForRoute = list(self.mapBoxScrap.keys())[i]
            self._calculate_distance(busServiceForRoute, key)

    def _populate_routes_information(self) -> None:
        for stopName in self.graphedData.keys():
            # Initialize arrays
            self.graphedData[stopName].append({"Buses Supported": []})
            self.graphedData[stopName].append({"Close Point": []})
            self.graphedData[stopName].append({"Stops Nearby": []})

            # Append routes information into return data
            for i in self.parsedData.keys():
                for d in range(len(self.parsedData[i]) - 1, -1, -1):
                    if stopName == self.parsedData[i][d]["Name"]:
                        self.graphedData[stopName][0]["Buses Supported"].append(i)
                        self.graphedData[stopName][1]["Close Point"].append(self.parsedData[i][d]["Closest Point"])
                        if d >= 1:
                            self.graphedData[stopName].append({
                                "Name": self.parsedData[i][d - 1]["Name"],
                                "Bus": i,
                                "Distance Away": float(self.parsedData[i][d - 1]["Distance to Next"])
                            })
                        break

            # Sanitize data
            self.graphedData[stopName][0]["Buses Supported"] = list(
                set(self.graphedData[stopName][0]["Buses Supported"]))
            self.graphedData[stopName][1]["Close Point"] = list(
                {tuple(x) for x in self.graphedData[stopName][1]["Close Point"]})

            for a in self.parsedData.keys():
                for d in self.parsedData[a]:
                    # Check for minimum distance between bus route point and bus stop
                    if self._calculate_relative_distance(
                            [d["Closest Point"][1], d["Closest Point"][0]],
                            [
                                self.graphedData[stopName][1]["Close Point"][0][1],
                                self.graphedData[stopName][1]["Close Point"][0][0]
                            ]
                    ) < 0.15 and d["Name"] != stopName:
                        self.graphedData[stopName][2]["Stops Nearby"].append(d["Name"])
            self.graphedData[stopName][2]["Stops Nearby"] = list(
                set(self.graphedData[stopName][2]["Stops Nearby"]))

    def _find_nearest_points(self, index: int, key: list) -> None:
        prevSave = 0
        # Calculate distances between bus stops
        for dataIndex in range(0, len(self.parsedData[key])):
            returnIndex = 0
            check = 5000  # Upper bound for distance between bus stop and bus route point
            point = None
            counter = 0
            # Iterate coordinates to calculate distances between bus stops
            for coordinates in range(prevSave, len(self.mapBoxScrap[list(self.mapBoxScrap.keys())[index]])):
                counter += 1
                # Limit for how many route points to check
                if counter == 51:
                    break
                busStop = self.parsedData[key][dataIndex]
                # Calculate distance between bus stop and bus route point
                distance = self._calculate_relative_distance(
                    (
                        float(busStop["GPS Location"].split(",")[0].strip()),
                        float(busStop["GPS Location"].split(",")[1].strip())
                    ),
                    (
                        float(self.mapBoxScrap[list(self.mapBoxScrap.keys())[index]][coordinates][1]),
                        float(self.mapBoxScrap[list(self.mapBoxScrap.keys())[index]][coordinates][0])
                    )
                )
                # Minimum distance filter
                if distance < check:
                    check = distance
                    # Bus route point with minimum distance from bus stop
                    point = self.mapBoxScrap[list(self.mapBoxScrap.keys())[index]][coordinates]
                    returnIndex = coordinates
                    prevSave = coordinates
            # Save closest bus route point from bus stop
            self.parsedData[key][dataIndex]['Distance Away'] = check
            self.parsedData[key][dataIndex]["Closest Point"] = point
            self.parsedData[key][dataIndex]["Index in route[]"] = returnIndex

    def _calculate_distance(self, busServiceForRoute: list, key: list) -> None:
        routeCounter = 0
        # Iterate bus stops
        for dataIndex in range(0, len(self.parsedData[key]) - 1):
            counterDist = 0
            # Iterate bus routes
            for routeIndexIterator in range(routeCounter, len(self.mapBoxScrap[busServiceForRoute]) - 1):
                origin = (
                    self.mapBoxScrap[busServiceForRoute][routeIndexIterator][1],
                    self.mapBoxScrap[busServiceForRoute][routeIndexIterator][0]
                )
                destination = (
                    self.mapBoxScrap[busServiceForRoute][routeIndexIterator + 1][1],
                    self.mapBoxScrap[busServiceForRoute][routeIndexIterator + 1][0]
                )
                # Calculate distance between origin and destination
                temp = self._calculate_relative_distance(origin, destination)
                counterDist += temp

                # Save distance from closest bus route point
                if self.parsedData[key][dataIndex + 1]["Closest Point"] == \
                        self.mapBoxScrap[busServiceForRoute][routeIndexIterator + 1]:
                    self.parsedData[key][dataIndex]["Distance to Next"] = counterDist
                    routeCounter = routeIndexIterator
                    break
                routeCounter = routeIndexIterator

    @staticmethod
    def _calculate_relative_distance(coordinate1, coordinate2) -> float:
        R = 6373.0  # earth
        lat1 = radians(float(coordinate1[0]))
        lon1 = radians(float(coordinate1[1]))
        lat2 = radians(float(coordinate2[0]))
        lon2 = radians(float(coordinate2[1]))
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Calculate distances between coordinates using latitudes and longitudes
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance


def main():
    routes = RoutingAlgo()

    # ---------- TESTING SCENARIOS, FEEL FREE TO ADD MORE --------------
    pp.pprint(routes.get_route("Kulai Terminal", "Senai Airport Terminal"))  # one of the furthest routes

    # pp.pprint(routes.get_route("Majlis Bandaraya Johor Bahru", "AEON Tebrau City")) #example 2
    # pp.pprint(routes.get_route("Taman Universiti Terminal", "Johor Islamic Complex")) #Single xfer
    # pp.pprint(routes.get_route("Hub PPR Sri Stulang", "AEON Tebrau City")) #Straight Route
    # pp.pprint(routes.get_route("81400 Senai, Johor, Malaysia", "No.4, Jalan Pendidikan, Taman Universiti, 81300 Johor Bahru, Johor, Malaysia"))


if __name__ == "__main__":
    main()

'''

def calcTime(distance, timeDeets, speed):
    openingTime = datetime.strptime(timeDeets["Daily"].split("-")[0].strip(), '%H:%M')
    closingTime = datetime.strptime(timeDeets["Daily"].split("-")[1].strip(), '%H:%M')
    timetaken = 0
    now = datetime.now()
    if openingTime.time() < now.time() < closingTime.time():
        for i in list(timeDeets.keys())[1:]:
            startTime = datetime.strptime(timeDeets[i].split("-")[0].strip(), '%H%M')
            endTime = datetime.strptime(timeDeets[i].split("-")[1].strip(), '%H%M')
            if startTime.time() <= now.time() <= endTime.time():
                timetaken = int(i)

    timetaken += (distance / 1000 / speed) * 60
    return timetaken

def calcBusToTake(place):
    start = time.time()
    # Search Algo needs to be improved
    busToTake = ""
    busStopToTake = ""
    distanceAway = 5000
    for i in self.parsedData.keys():
        for stop in self.parsedData[i]:
            temp = self._calculate_relative_distance(place, [stop["Closest Point"][1], stop["Closest Point"][0]])
            if temp <= distanceAway:
                distanceAway = temp
                busToTake = i
                busStopToTake = stop["Name"]
    print("Bus to Take: " + busToTake + " going towards " + self.parsedData[busToTake][-1]["Name"])
    print("Bus Stop to Take: " + busStopToTake)

def giveRoute(fromHere, toHere):
    with open('../web_scraper/routes.bin', 'rb') as f:
        routes = pickle.load(f)
        closestDistanceFrom = P101BusStops[1]["Coordinates"]
        closestDistanceTo = P101BusStops[1]["Coordinates"]
        startingBusStop = P101BusStops[1]
        endingBusStop = P101BusStops[1]

        for i in P101BusStops[1:]:
            if self._calculate_relative_distance(fromHere, closestDistanceFrom) > self._calculate_relative_distance(fromHere, i["Coordinates"]):
                startingBusStop = i
                closestDistanceFrom = i["Coordinates"]

            if self._calculate_relative_distance(toHere, closestDistanceTo) > self._calculate_relative_distance(toHere, i["Coordinates"]):
                endingBusStop = i
                closestDistanceTo = i["Coordinates"]
        distance = startingBusStop["DistanceToNext"]
        indexOfStart = P101BusStops.index(startingBusStop)
        indexOfEnd = P101BusStops.index(endingBusStop)
        for i in range(indexOfStart + 1, indexOfEnd):
            distance += P101BusStops[i]["DistanceToNext"]

        avgSpeed = 45  # Not good as highway speed != normal road speed
        timetaken = calcTime(distance, P101BusStops[0], avgSpeed)
        numberofStops = P101BusStops.index(endingBusStop) - P101BusStops.index(startingBusStop)
        print("You will need to start from: " + startingBusStop["Name"])
        print("You will go through " + str(numberofStops) + " stops")
        print("And you will end up at: " + endingBusStop["Name"])
        print("Time taken will be around " + str(timetaken) + " minutes.")
        print("The distance travelled will be " + str(distance / 1000) + "KM")

        listOfReturnRoute = []
        for i in routes["P101_1"][routes["P101_1"].index(startingBusStop["Closest Point"]):routes["P101_1"].index(
                endingBusStop["Closest Point"]) + 1]:
            listOfReturnRoute.append(i)

        toReturn = {
            "Starting Bus Stop": startingBusStop,
            "Ending Bus Stop": endingBusStop,
            "Route Taken": listOfReturnRoute,
            "Distance Travelled": distance,
            "Distance Travelled (KM)": distance / 1000,
            "Time Taken": timetaken
        }
        return toReturn

'''
