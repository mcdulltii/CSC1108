import os
import sys
import time
import pickle
from typing import List, Dict, Any

import googlemaps
import pprint as pp
from math import sin, cos, sqrt, atan2, radians

from datetime import datetime, timedelta

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

    def get_route(self, startingLocation: str, endingLocation: str) -> List[Dict[str, List[Any]]]:
        '''
        {
            Starting Bus Stop: startBusStop,
            Ending Bus Stop: endBusStop,
            Buses To Take: listOfBusesToTake, if there is more than 1 means there's a transfer,
            Route Taken: {Bus number: [list of routes...], Bus number 2: [list of routes....],
            Distance Travelled (KM) : distance travelled
        }
        '''
        toReturn = {
            "Routes": []
        }
        # GET COORDINATES FROM STRING GEOCODING
        startingLocationCoords = self.walkingRouteCalculator.string_to_coordinate(startingLocation)
        endingLocationCoords = self.walkingRouteCalculator.string_to_coordinate(endingLocation)

        startingCloseBusStop = self.walkingRouteCalculator.find_nearby(startingLocationCoords)
        startingBusStop = startingCloseBusStop[1]["Name"]
        gpsBusStopStart = startingCloseBusStop[1]["GPS Location"].split(", ")

        endingCloseBusStop = self.walkingRouteCalculator.find_nearby(endingLocationCoords)
        endingBusStop = endingCloseBusStop[1]["Name"]
        gpsBusStopEnd = endingCloseBusStop[1]["GPS Location"].split(", ")

        if self._calculate_relative_distance(startingLocationCoords, gpsBusStopStart) < 0.10:
            toReturn["Routes"].append(
                {
                    "Route": [{'lat': i[1],'lng': i[0]} for i in startingCloseBusStop[0]],
                    "Type": "Walking",
                    "Start": startingLocation,
                    "End": startingBusStop
                }
            )

        routeObject = self.routeCalculator.calculate_route(startingBusStop, endingBusStop)

        # print("Walking Route to " + startingBusStop + ":" + str(startingCloseBusStop[0]))
        timenow = datetime.now()
        busStopStart = routeObject["Pathing"][0]
        toReturn["Time Taken"] = routeObject["Distance"]
        toReturn["Time Start"] = timenow.strftime("%H:%M:%S")
        timeToAdd = timedelta(minutes=routeObject["Distance"])
        toReturn["Time End"] = (timenow + timeToAdd).strftime("%H:%M:%S")
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
            busStopStart = self._find_bus_stop_information(busesToTake[0], busStopStart)
            busPointToCheck = busStopStart["Closest Point"]
            if transferObject is not None:
                if transferObject["Type"] == "Walking":
                    busStopEnd = transferObject["Transfer Stop From"]
                else:
                    busStopEnd = transferObject["Transfer Stop"]
            else:
                busStopEnd = routeObject["Pathing"][-1]
            busStopEndInfo = self._find_bus_stop_information(busesToTake[0], busStopEnd)
            # print(busStopEndInfo)
            busPointEnd = busStopEndInfo["Closest Point"]

            indexOf = list(self.parsedData.keys()).index(busesToTake[0])
            correspondingMapBoxKey = list(self.mapBoxScrap.keys())[indexOf]
            pointIterator = 0

            indexOfRouteObj = next(
                (index for (index, d) in enumerate(toReturn["Routes"]) if d["Type"] == busesToTake[0]), None)
            toReturn["Routes"][indexOfRouteObj]["Start"] = busStopStart["Name"]
            toReturn["Routes"][indexOfRouteObj]["End"] = busStopEnd
            startRecording = False
            while True:
                point = self.mapBoxScrap[correspondingMapBoxKey][pointIterator]
                if point == busPointToCheck:
                    # print("MATCH")
                    startRecording = True
                if startRecording:
                    toReturn["Routes"][indexOfRouteObj]["Route"].append({'lat': point[1], 'lng': point[0]})
                if point == busPointEnd and startRecording:
                    if transferObject is not None:
                        if transferObject["Type"] == "Walking":
                            busStopStart = transferObject["Transfer Stop To"]  # to bus stop so coordinates end
                            nextBus = routeObject["Buses To Return"][
                                routeObject["Buses To Return"].index(busesToTake) + 1]
                            busInformationForFrom = self._find_bus_stop_information(busesToTake[0], transferObject[
                                "Transfer Stop From"])
                            busInformationForTo = self._find_bus_stop_information(nextBus[0], busStopStart)
                            coordinatesStart = busInformationForFrom["GPS Location"]
                            coordinatesEnd = busInformationForTo["GPS Location"]

                            toReturn["Routes"].append({
                                "Route": [{'lat': i[1],'lng': i[0]} for i in self.walkingRouteCalculator.get_walking_route(coordinatesStart, coordinatesEnd)],
                                "Type": "Walking",
                                "Start": transferObject["Transfer Stop From"],
                                "End": busStopStart
                            })
                        else:
                            busStopStart = transferObject["Transfer Stop"]
                    break
                pointIterator += 1

                if pointIterator == len(self.mapBoxScrap[correspondingMapBoxKey]):
                    # print("reset")
                    pointIterator = 0
        if self._calculate_relative_distance(endingLocationCoords,
                                             gpsBusStopEnd) > 0.00:
            endingCloseBusStop[0].insert(0,gpsBusStopEnd)
            endingCloseBusStop[0].append(endingLocationCoords)
            toReturn["Routes"].append(
                {
                    "Route": [{'lat': i[1],'lng': i[0]} for i in endingCloseBusStop[0]],
                    "Type": "Walking",
                    "Start": endingBusStop,
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
                                "Distance Away": float(self.parsedData[i][d - 1]["Distance to Next"]),
                                "Time Taken" : float(self.parsedData[i][d - 1]["Time Taken"])
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
                if counter == 100:
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
                    self.parsedData[key][dataIndex]["Time Taken"] = self._calculate_time_taken(counterDist)
                    routeCounter = routeIndexIterator
                    break
                routeCounter = routeIndexIterator

    def _find_bus_stop_information(self, busServiceForRoute, busStopName):
        indexOfBusStop = next(
            (index for (index, d) in enumerate(self.parsedData[busServiceForRoute]) if
             d["Name"] == busStopName), None)

        busStopToReturn = self.parsedData[busServiceForRoute][indexOfBusStop]
        return busStopToReturn

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

    @staticmethod
    def _calculate_time_taken(distance):
        return distance / 50 * 60


def main():
    routes = RoutingAlgo()

    # ---------- TESTING SCENARIOS, FEEL FREE TO ADD MORE --------------
    pp.pprint(routes.get_route("Jalan Kampung Maju Jaya, Senai,JHR,Malaysia", "Jalan Stulang Laut, Johor Bahru,JHR,Malaysia"))  # one of the furthest routes
    # P403-loop -> P211-01 -> P101-loop -> P102-02 -> P102-01
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
