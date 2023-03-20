import pickle
import googlemaps
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime
import time
from dijkstras import Dijkstras
from routes_reader.routes_reader import RoutesReader

routes_reader = RoutesReader()

parsedData = {}


class RoutingAlgo:
    gmaps = None
    mapBoxScrap = None
    busstops = None
    graphedData = {}
    routeCalculator = None

    def __init__(self):
        self.gmaps = googlemaps.Client("AIzaSyAB_QsjZviwHVJHyBCeTPiK8M1NOvSLcns")
        self.busstops = routes_reader.read_excel('bus_stops.xlsx')
        with open('../web_scraper/routes.bin', 'rb') as f:
            self.mapBoxScrap = pickle.load(f)
        for i in range(0, len(self.busstops)):
            parsedData[list(self.busstops.keys())[i]] = []
            for l, stop in self.busstops[list(self.busstops.keys())[i]].iterrows():
                parsedData[list(self.busstops.keys())[i]].append(
                    {
                        "Name": stop["Bus stop"],
                        "GPS Location": stop["GPS Location"]
                    }
                )
                self.graphedData[stop["Bus stop"]] = []
            key = list(parsedData.keys())[i]
            prevSave = 0
            for dataIndex in range(0, len(parsedData[key])):
                returnIndex = 0
                check = 5000
                point = None
                counter = 0
                for coordinates in range(prevSave, len(self.mapBoxScrap[list(self.mapBoxScrap.keys())[i]])):
                    counter += 1
                    if (counter == 51):
                        break
                    busStop = parsedData[key][dataIndex]
                    distance = calcDistance(
                        (float(busStop["GPS Location"].split(",")[0].strip()),
                         float(busStop["GPS Location"].split(",")[1].strip())),
                        (float(self.mapBoxScrap[list(self.mapBoxScrap.keys())[i]][coordinates][1]),
                         float(self.mapBoxScrap[list(self.mapBoxScrap.keys())[i]][coordinates][0])))
                    if distance < check:
                        check = distance
                        point = self.mapBoxScrap[list(self.mapBoxScrap.keys())[i]][coordinates]
                        returnIndex = coordinates
                        prevSave = coordinates
                parsedData[key][dataIndex]['Distance Away'] = check
                parsedData[key][dataIndex]["Closest Point"] = point
                parsedData[key][dataIndex]["Index in route[]"] = returnIndex
            busServiceForRoute = list(self.mapBoxScrap.keys())[i]
            routeCounter = 0
            for dataIndex in range(0, len(parsedData[key]) - 1):
                counterDist = 0
                for routeIndexIterator in range(routeCounter, len(self.mapBoxScrap[busServiceForRoute]) - 1):
                    origin = (self.mapBoxScrap[busServiceForRoute][routeIndexIterator][1],
                              self.mapBoxScrap[busServiceForRoute][routeIndexIterator][0])
                    destination = (
                        self.mapBoxScrap[busServiceForRoute][routeIndexIterator + 1][1],
                        self.mapBoxScrap[busServiceForRoute][routeIndexIterator + 1][0])
                    # temp = gmaps.distance_matrix(origin, destination, mode="driving")["rows"][0]["elements"][0][

                    #    "distance"][
                    #   "value"]
                    temp = calcDistance(origin, destination)
                    counterDist += temp

                    if parsedData[key][dataIndex + 1]["Closest Point"] == self.mapBoxScrap[busServiceForRoute][
                        routeIndexIterator + 1]:
                        parsedData[key][dataIndex]["Distance to Next"] = counterDist
                        routeCounter = routeIndexIterator
                        break
                    routeCounter = routeIndexIterator
        for stopName in self.graphedData.keys():
            self.graphedData[stopName].append({"Buses Supported": []})
            self.graphedData[stopName].append({"Close Point": []})
            self.graphedData[stopName].append({"Stops Nearby": []})

            # self.graphedData[stopName].append({"Close Bus Stops": []})
            for i in parsedData.keys():
                for d in range(len(parsedData[i]) - 1, -1, -1):
                    if stopName == parsedData[i][d]["Name"]:
                        self.graphedData[stopName][0]["Buses Supported"].append(i)
                        self.graphedData[stopName][1]["Close Point"].append(parsedData[i][d]["Closest Point"])
                        if d >= 1:
                            self.graphedData[stopName].append({
                                "Name": parsedData[i][d - 1]["Name"],
                                "Bus": i,
                                "Distance Away": float(parsedData[i][d - 1]["Distance to Next"])
                            })
                        break

            """for i in parsedData.keys():
                for d in range(0, len(parsedData[i])):"""

            self.graphedData[stopName][0]["Buses Supported"] = list(
                set(self.graphedData[stopName][0]["Buses Supported"]))
            self.graphedData[stopName][1]["Close Point"] = list({tuple(x) for x in
                                                                 self.graphedData[stopName][1]["Close Point"]})
            for a in parsedData.keys():
                for d in parsedData[a]:
                    if calcDistance(
                            [d["Closest Point"][1], d["Closest Point"][0]],
                            [self.graphedData[stopName][1]["Close Point"][0][1],
                             self.graphedData[stopName][1]["Close Point"][0][0]]) < 0.15 and d["Name"] != stopName:
                        self.graphedData[stopName][2]["Stops Nearby"].append(d["Name"])
            self.graphedData[stopName][2]["Stops Nearby"] = list(
                set(self.graphedData[stopName][2]["Stops Nearby"]))

        self.routeCalculator = Dijkstras(self.graphedData)

    def getRoute(self, startingLocation, endingLocation):
        routeObject = self.routeCalculator.calculateRoute(startingLocation, endingLocation)
        # Anis Method to be called Here
        startingBusStop = startingLocation
        endingBusStop = endingLocation
        print("Starting Location: " + startingLocation)
        print("Ending Location: " + endingLocation)

        toReturn = {
            "Starting Bus Stop": startingBusStop,
            "Ending Bus Stop": endingBusStop,
            "Buses To Take": [],
            "Route Taken": [],
            "Transfer Bus Stops": [],
            "Distance Travelled (KM)": routeObject["Distance"]
        }
        print(routeObject)

        for i in routeObject["Transfers"]:
            toReturn["Buses To Take"].append(i["Transfer From"])
            toReturn["Buses To Take"].append(i["Transfer To"])
            toReturn["Transfer Bus Stops"].append(i["TransferStop"])
        toReturn["Buses To Take"] = list(list(dict.fromkeys(toReturn["Buses To Take"])))
        if len(toReturn["Buses To Take"]) == 1:
            toReturn["Transfer Bus Stops"] = ""
        xferBusStop = startingBusStop

        for i in range(0, len(toReturn["Buses To Take"])):
            stopInfo = next((item for item in parsedData[toReturn["Buses To Take"][i]] if item["Name"] == xferBusStop),
                            None)
            toReturn["Route Taken"].append({})
            toReturn["Route Taken"][i][toReturn["Buses To Take"][i]] = []

            if i < len(toReturn["Transfer Bus Stops"]):
                xferBusStop = toReturn["Transfer Bus Stops"][i]
            else:
                xferBusStop = endingBusStop
            nextStopInfo = next(
                (item for item in parsedData[toReturn["Buses To Take"][i]] if item["Name"] == xferBusStop), None)
            start = False

            for d in self.mapBoxScrap[
                list(self.mapBoxScrap.keys())[list(parsedData.keys()).index(toReturn["Buses To Take"][i])]]:
                if d == nextStopInfo["Closest Point"]:
                    break
                if start:
                    toReturn["Route Taken"][i][toReturn["Buses To Take"][i]].append(d)
                else:
                    if d == stopInfo["Closest Point"]:
                        start = True
        '''
        {
            Starting Bus Stop: startBusStop,
            Ending Bus Stop: endBusStop,
            Buses To Take: listOfBusesToTake, if there is more than 1 means there's a transfer,
            Route Taken: {Bus number: [list of routes...], Bus number 2: [list of routes....],
            Distance Travelled (KM) : distance travelled
        }
        '''
        print(toReturn)
        return toReturn


def calcDistance(coordinate1, coordinate2):
    R = 6373.0  # earth
    lat1 = radians(float(coordinate1[0]))
    lon1 = radians(float(coordinate1[1]))
    lat2 = radians(float(coordinate2[0]))
    lon2 = radians(float(coordinate2[1]))
    dlon = lon2 - lon1
    dlat = lat2 - lat1;

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


testing = RoutingAlgo()
# ---------- TESTING SCENARIOS, FEEL FREE TO ADD MORE --------------
#testing.getRoute("Kulai Terminal", "Lotus Plentong (Tesco Extra)") #one of the furthest routes
#testing.getRoute("Majlis Bandaraya Johor Bahru", "AEON Tebrau City")
#testing.getRoute("Taman Universiti Terminal", "Johor Islamic Complex") #Single xfer
#testing.getRoute("Hub PPR Sri Stulang", "AEON Tebrau City") #Straight Route




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
    for i in parsedData.keys():
        for stop in parsedData[i]:
            temp = calcDistance(place, [stop["Closest Point"][1], stop["Closest Point"][0]])
            if temp <= distanceAway:
                distanceAway = temp
                busToTake = i
                busStopToTake = stop["Name"]
    print("Bus to Take: " + busToTake + " going towards " + parsedData[busToTake][-1]["Name"])
    print("Bus Stop to Take: " + busStopToTake)

def giveRoute(fromHere, toHere):
    with open('../web_scraper/routes.bin', 'rb') as f:
        routes = pickle.load(f)
        closestDistanceFrom = P101BusStops[1]["Coordinates"]
        closestDistanceTo = P101BusStops[1]["Coordinates"]
        startingBusStop = P101BusStops[1]
        endingBusStop = P101BusStops[1]

        for i in P101BusStops[1:]:
            if calcdistance(fromHere, closestDistanceFrom) > calcdistance(fromHere, i["Coordinates"]):
                startingBusStop = i
                closestDistanceFrom = i["Coordinates"]

            if calcdistance(toHere, closestDistanceTo) > calcdistance(toHere, i["Coordinates"]):
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
