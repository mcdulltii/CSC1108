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
from routing.AStarAlgo import AStar
from routing.shortest_walk import shortest_walk
from collections import deque


class RoutingAlgo:
    # Variable declarations
    busstops = None
    mapBoxScrap = None
    routes_reader = None
    routeCalculator = None
    walkingRouteCalculator = None
    backwardGraphedData = {}
    forwardGraphedData = {}
    parsedData = {}
    frequencyData = {}

    def __init__(self) -> None:
        # Initialize RoutesReader class
        self.routes_reader = RoutesReader()
        # Read bus stops from excel
        self.busstops = self.routes_reader.read_excel('bus_stops.xlsx')
        # Load bus routes from file
        dirpath = os.path.dirname(os.path.realpath(__file__))
        routes_path = os.path.join(dirpath, "../web_scraper/routes.bin")
        frequency_path = os.path.join(dirpath, "../web_scraper/freq.bin")
        with open(routes_path, 'rb') as f:
            self.mapBoxScrap = pickle.load(f)
        with open(frequency_path, 'rb') as f:
            self.frequencyData = pickle.load(f)
        self._load_bus_stops()
        self.walkingRouteCalculator = shortest_walk(self.parsedData)

        self._populate_routes_information()
        self.DijkstrasrouteCalculator = Dijkstras(self.backwardGraphedData)
        self.AStarrouteCalculator = AStar(self.forwardGraphedData)

    def get_route(self, startingLocation: str, endingLocation: str) -> List[Dict[str, List[Any]]]:

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
        # Invert ending walking route
        endingCloseBusStop[0] = endingCloseBusStop[0][::-1]
        endingBusStop = endingCloseBusStop[1]["Name"]
        gpsBusStopEnd = endingCloseBusStop[1]["GPS Location"].split(", ")
        routeObjects = [self.DijkstrasrouteCalculator.calculate_route(startingBusStop, endingBusStop), self.AStarrouteCalculator.calculate_route(startingBusStop, endingBusStop)]
        returnRoutes = []

        for routeObject in routeObjects:
            print(routeObject)
            timeStart = "095511"
            timeToAdd = 0
            timeTravelling = routeObject["Distance"]

            if self._calculate_relative_distance(startingLocationCoords, gpsBusStopStart) > 0.10:
                toReturn["Routes"].append(
                    {
                        "Route": [{'lat': i[0], 'lng': i[1]} for i in startingCloseBusStop[0]],
                        "Type": "Walking",
                        "Start": startingLocation,
                        "End": startingBusStop,
                        "Start Arrival Time": timeStart,
                        "Distance Travelled": startingCloseBusStop[2],
                        "Time Taken": startingCloseBusStop[3]
                    }

                )
                timeStart = self._calculating_time(timeStart, startingCloseBusStop[3], 1)
                timeTravelling += startingCloseBusStop[3]
                timeToAdd += startingCloseBusStop[3]
                toReturn["Routes"][0]["End Arrival Time"] = timeStart

            busStopStart = routeObject["Pathing"][0]
            toReturn["Time Start"] = timeStart
            transfers = deque()
            for transfer in routeObject["Transfers"]:
                transfers.append(transfer)
            for busesToTake in routeObject["Buses To Return"]:
                timeToCatch = self._find_nearest_arrival_time(busesToTake[0], busStopStart, timeStart)
                toReturn["Routes"].append({
                    "Type": busesToTake[0],
                    "Route": [],
                    "Start Arrival Time": timeStart,
                    "Bus Arrival Time": timeToCatch
                })
                transferObject = None
                if len(transfers) != 0:
                    transferObject = transfers.popleft()
                timeStart = timeToCatch
                busStopStart = self._find_bus_stop_information(busesToTake[0], busStopStart)
                busPointToCheck = busStopStart["Closest Point"]
                if transferObject is not None:
                    if transferObject["Type"] == "Walking":
                        busStopEnd = transferObject["Transfer Stop From"]
                        timeStart = self._calculating_time(timeStart, transferObject["Time Taken for Bus"], 1)
                        timeToAdd += transferObject["Time Taken for Bus"]
                    else:
                        busStopEnd = transferObject["Transfer Stop"]
                        timeStart = self._calculating_time(timeStart, transferObject["Time Taken"], 1)
                        timeToAdd += transferObject["Time Taken"]
                else:
                    timeStart = self._calculating_time(timeStart, (timeTravelling - timeToAdd), 1)
                    busStopEnd = routeObject["Pathing"][-1]
                busStopEndInfo = self._find_bus_stop_information(busesToTake[0], busStopEnd)
                busPointEnd = busStopEndInfo["Closest Point"]
                indexOf = list(self.parsedData.keys()).index(busesToTake[0])
                correspondingMapBoxKey = list(self.mapBoxScrap.keys())[indexOf]
                pointIterator = 0

                indexOfRouteObj = next(
                    (index for (index, d) in enumerate(toReturn["Routes"]) if d["Type"] == busesToTake[0]), None)
                toReturn["Routes"][indexOfRouteObj]["Start"] = busStopStart["Name"]
                toReturn["Routes"][indexOfRouteObj]["End"] = busStopEnd
                busInBetweenInfo = self._get_number_of_stops(routeObject["Pathing"],
                                                             busStopStart["Name"],
                                                             busStopEnd, busesToTake[0])
                toReturn["Routes"][indexOfRouteObj]["Number Of Stops"] = busInBetweenInfo[0]
                toReturn["Routes"][indexOfRouteObj]["Stops In Between"] = busInBetweenInfo[1]
                toReturn["Routes"][indexOfRouteObj]["End Arrival Time"] = timeStart
                toReturn["Routes"][indexOfRouteObj]["Time Taken"] = self._calculating_time(
                    toReturn["Routes"][indexOfRouteObj]["Bus Arrival Time"],
                    toReturn["Routes"][indexOfRouteObj]["End Arrival Time"], 3)

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
                                coordinatesStart = [float(x) for x in busInformationForFrom["GPS Location"].split(", ")]
                                coordinatesEnd = [float(x) for x in busInformationForTo["GPS Location"].split(", ")]
                                returnWalkingRouteCalc = self.walkingRouteCalculator.get_walking_route(coordinatesStart,
                                                                                                       coordinatesEnd)
                                toReturn["Routes"].append({
                                    "Route": [{'lat': i[0], 'lng': i[1]} for i in
                                              returnWalkingRouteCalc[0]],
                                    "Type": "Walking",
                                    "Start": transferObject["Transfer Stop From"],
                                    "End": busStopStart,
                                    "Time Taken": returnWalkingRouteCalc[2],
                                    "Start Arrival Time": timeStart,
                                    "Distance Travelled": returnWalkingRouteCalc[1]
                                })
                                timeToAdd += returnWalkingRouteCalc[2]
                                timeTravelling += returnWalkingRouteCalc[2]

                                timeStart = self._calculating_time(timeStart, returnWalkingRouteCalc[2], 1)
                                toReturn["Routes"][indexOfRouteObj + 1]["End Arrival Time"] = timeStart
                            else:
                                busStopStart = transferObject["Transfer Stop"]
                        break
                    pointIterator += 1

                    if pointIterator == len(self.mapBoxScrap[correspondingMapBoxKey]):
                        pointIterator = 0
            if self._calculate_relative_distance(endingLocationCoords,
                                                 gpsBusStopEnd) > 0.10:
                endingCloseBusStop[0].insert(0, list(map(float, gpsBusStopEnd)))
                endingCloseBusStop[0].append(endingLocationCoords)
                toReturn["Routes"].append(
                    {
                        "Route": [{'lat': i[0], 'lng': i[1]} for i in endingCloseBusStop[0]],
                        "Type": "Walking",
                        "Start Arrival Time": timeStart,
                        "Start": endingBusStop,
                        "End": endingLocation,
                        "Distance Travelled": endingCloseBusStop[2],
                        "Time Taken": endingCloseBusStop[3]
                    }
                )
                timeStart = (datetime.strptime(timeStart, "%H%M%S") + timedelta(
                    minutes=endingCloseBusStop[3])).strftime("%H%M%S")
                toReturn["Routes"][-1]["End Arrival Time"] = timeStart
                toReturn["Time End"] = timeStart
            timeConvertedEnd = datetime.strptime(toReturn["Time End"], "%H%M%S")
            timeConvertedStart = datetime.strptime(toReturn["Time Start"], "%H%M%S")
            toReturn["Time Taken"] = ((timeConvertedEnd - timeConvertedStart).total_seconds()) / 60
            toReturn["Restaurants Nearby End"] = self._get_closest_restaurants(endingLocation)
            toReturn["Embassies Nearby End"] = self._get_closest_embassy(endingLocation)
            toReturn["Police Stations Nearby End"] = self._get_closest_police_stations(endingLocation)
            toReturn["Bar Nearby End"] = self._get_closest_bar(endingLocation)

            returnRoutes.append(toReturn)

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
                self.backwardGraphedData[stop["Bus stop"]] = []
                self.forwardGraphedData[stop["Bus stop"]] = []

            key = list(self.parsedData.keys())[i]

            # Find the nearest point in bus route from bus stop coordinate
            self._find_nearest_points(i, key)
            # Calculate distance
            busServiceForRoute = list(self.mapBoxScrap.keys())[i]
            self._calculate_distance(busServiceForRoute, key)
            self._get_arrival_time(i, key)

    def _populate_routes_information(self) -> None:
        for stopName in self.forwardGraphedData.keys():
            self.forwardGraphedData[stopName].append({"Buses Supported": []})
            self.forwardGraphedData[stopName].append({"Close Point": []})
            self.forwardGraphedData[stopName].append({"Stops Nearby": []})

            for i in self.parsedData.keys():
                for d in range(0, len(self.parsedData[i])):
                    if stopName == self.parsedData[i][d]["Name"]:
                        self.forwardGraphedData[stopName][0]["Buses Supported"].append(i)
                        self.forwardGraphedData[stopName][1]["Close Point"].append(
                            self.parsedData[i][d]["Closest Point"])
                        if d != len(self.parsedData[i]) -1:
                            self.forwardGraphedData[stopName].append({
                                "Name": self.parsedData[i][d + 1]["Name"],
                                "Bus": i,
                                "Distance Away": float(self.parsedData[i][d]["Distance to Next"]),
                                "Time Taken": float(self.parsedData[i][d]["Time Taken"])
                            })
                        break

        for stopName in self.backwardGraphedData.keys():
            # Initialize arrays
            self.backwardGraphedData[stopName].append({"Buses Supported": []})
            self.backwardGraphedData[stopName].append({"Close Point": []})
            self.backwardGraphedData[stopName].append({"Stops Nearby": []})

            # Append routes information into return data
            for i in self.parsedData.keys():
                for d in range(len(self.parsedData[i]) - 1, -1, -1):
                    if stopName == self.parsedData[i][d]["Name"]:
                        self.backwardGraphedData[stopName][0]["Buses Supported"].append(i)
                        self.backwardGraphedData[stopName][1]["Close Point"].append(
                            self.parsedData[i][d]["Closest Point"])
                        if d >= 1:
                            self.backwardGraphedData[stopName].append({
                                "Name": self.parsedData[i][d - 1]["Name"],
                                "Bus": i,
                                "Distance Away": float(self.parsedData[i][d - 1]["Distance to Next"]),
                                "Time Taken": float(self.parsedData[i][d - 1]["Time Taken"])
                            })
                        break

            for a in self.parsedData.keys():
                for d in self.parsedData[a]:
                    # Check for minimum distance between bus route point and bus stop
                    if self._calculate_relative_distance(
                            [d["Closest Point"][1], d["Closest Point"][0]],
                            [
                                self.forwardGraphedData[stopName][1]["Close Point"][0][1],
                                self.forwardGraphedData[stopName][1]["Close Point"][0][0]
                            ]
                    ) < 0.15 and d["Name"] != stopName:
                        self.forwardGraphedData[stopName][2]["Stops Nearby"].append(d["Name"])

            for a in self.parsedData.keys():
                for d in self.parsedData[a]:
                    # Check for minimum distance between bus route point and bus stop
                    if self._calculate_relative_distance(
                            [d["Closest Point"][1], d["Closest Point"][0]],
                            [
                                self.backwardGraphedData[stopName][1]["Close Point"][0][1],
                                self.backwardGraphedData[stopName][1]["Close Point"][0][0]
                            ]
                    ) < 0.15 and d["Name"] != stopName:
                        self.backwardGraphedData[stopName][2]["Stops Nearby"].append(d["Name"])
            # Sanitize data
            self.backwardGraphedData[stopName][0]["Buses Supported"] = list(
                set(self.backwardGraphedData[stopName][0]["Buses Supported"]))
            self.backwardGraphedData[stopName][1]["Close Point"] = list(
                {tuple(x) for x in self.backwardGraphedData[stopName][1]["Close Point"]})
            self.backwardGraphedData[stopName][2]["Stops Nearby"] = list(
                set(self.backwardGraphedData[stopName][2]["Stops Nearby"]))

            self.forwardGraphedData[stopName][0]["Buses Supported"] = list(
                set(self.forwardGraphedData[stopName][0]["Buses Supported"]))
            self.forwardGraphedData[stopName][1]["Close Point"] = list(
                {tuple(x) for x in self.forwardGraphedData[stopName][1]["Close Point"]})
            self.forwardGraphedData[stopName][2]["Stops Nearby"] = list(
                set(self.forwardGraphedData[stopName][2]["Stops Nearby"]))

    def _get_number_of_stops(self, path, start, end, bus):

        startRecording = False
        count = 0
        listOfBusStops = []
        for i in path:
            if startRecording == True:
                busObjToAppend = self._find_bus_stop_information(bus, i)
                listOfBusStops.append({"Name": busObjToAppend["Name"], "Coordinates": busObjToAppend["GPS Location"]})
                count += 1
            if i == start:
                startRecording = True
            if i == end:
                break
        return (count, listOfBusStops)

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

    def _get_arrival_time(self, index: int, key: list):
        freqKey = list(self.frequencyData.keys())
        frequencyData = self.frequencyData[self._convert_to_key(freqKey, key)][0]
        for dataIndex in range(0, len(self.parsedData[key])):
            if dataIndex == 0:
                self.parsedData[key][dataIndex]["Time Of Arrival"] = []
                for frequency in frequencyData["Frequency"]:
                    self.parsedData[key][dataIndex]["Time Of Arrival"].append(frequency + "00")
            else:
                prevStopData = self.parsedData[key][dataIndex - 1]
                self.parsedData[key][dataIndex]["Time Of Arrival"] = []
                for times in prevStopData["Time Of Arrival"]:
                    prevTime = datetime.strptime(times, '%H%M%S')
                    timeToAdd = timedelta(minutes=prevStopData["Time Taken"])
                    self.parsedData[key][dataIndex]["Time Of Arrival"].append((prevTime + timeToAdd).strftime("%H%M%S"))

    def _find_nearest_arrival_time(self, bus, stopName, timeToCompare):
        busStopInfo = self._find_bus_stop_information(bus, stopName)
        timeToCompare = datetime.strptime(timeToCompare, "%H%M%S")
        timeToReturn = None
        differenceInTime = 500000000
        for index, time in enumerate(busStopInfo["Time Of Arrival"]):
            timeConverted = datetime.strptime(time, "%H%M%S")
            differenceInSeconds = (timeConverted - timeToCompare).total_seconds()
            if differenceInTime > differenceInSeconds >= 0:
                differenceInTime = differenceInSeconds
                timeToReturn = time
        return timeToReturn

    # temp Solution
    def _convert_to_key(self, freqKey, key):
        for i in freqKey:
            if i[0:4] == key[0:4]:
                return i

    def _find_bus_stop_information(self, busServiceForRoute, busStopName):
        indexOfBusStop = next(
            (index for (index, d) in enumerate(self.parsedData[busServiceForRoute]) if
             d["Name"] == busStopName), None)
        print(busStopName)
        print(busServiceForRoute)
        print(indexOfBusStop)
        busStopToReturn = self.parsedData[busServiceForRoute][indexOfBusStop]
        return busStopToReturn

    # Recomendations for USer
    def _get_closest_restaurants(self, location):
        return self.walkingRouteCalculator.find_nearest_point_of_interest(location, "Restaurant")

    def _get_closest_police_stations(self, location):
        return self.walkingRouteCalculator.find_nearest_point_of_interest(location, "Police Station")

    def _get_closest_bar(self, location):
        return self.walkingRouteCalculator.find_nearest_point_of_interest(location, "Bar")

    def _get_closest_embassy(self, location):
        return self.walkingRouteCalculator.find_nearest_point_of_interest(location, "Embassy")

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

    @staticmethod
    def _calculating_time(startingTime, operandInMinutes, addorminus):
        if (addorminus == 0):
            toReturnTime = (datetime.strptime(startingTime, "%H%M%S") - timedelta(
                minutes=operandInMinutes)).strftime("%H%M%S")
        if (addorminus == 3):
            toReturnTime = (datetime.strptime(operandInMinutes, "%H%M%S") - datetime.strptime(startingTime,
                                                                                              "%H%M%S")).total_seconds() / 60
        else:
            toReturnTime = (datetime.strptime(startingTime, "%H%M%S") + timedelta(
                minutes=operandInMinutes)).strftime("%H%M%S")
        return toReturnTime


def main():
    routes = RoutingAlgo()
    # routes.walkingRouteCalculator.find_nearest_restaurants("Larkin Terminal")

    # ---------- TESTING SCENARIOS, FEEL FREE TO ADD MORE --------------
    pp.pprint(routes.get_route("AEON Tebrau City", "Senai Airport"))  # one of the furthest routes
    # P403-loop -> P211-01 -> P101-loop -> P102-02 -> P102-01
    # pp.pprint(routes.get_route("Jalan Kampung Maju Jaya, Senai,JHR,Malaysia", "Jalan Stulang Baru, Johor Bahru,JHR,Malaysia")) #example 2
    # pp.pprint(routes.get_route("Taman Universiti", "Johor Islamic Complex")) #Single xfer
    # pp.pprint(routes.get_route("Hub PPR Sri Stulang"tr, "AEON Tebrau City")) #Straight Route
    # pp.pprint(routes.get_route("81400 Senai, Johor, Malaysia", "No.4, Jalan Pendidikan, Taman Universiti, 81300 Johor Bahru, Johor, Malaysia"))


if __name__ == "__main__":
    main()
