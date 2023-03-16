import pickle
import googlemaps
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime
import time
import dijkstras
from routes_reader.routes_reader import RoutesReader

routes_reader = RoutesReader()

busstops = routes_reader.read_excel('bus_stops.xlsx')
P101BusStops = busstops["P101-loop"]
parsedData = {}
graphedData = {}
mapBoxScrap = None

def calcdistance(coordinate1, coordinate2):
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


def preprocessing():
    with open('../web_scraper/routes.bin', 'rb') as f:
        routes = pickle.load(f)
        mapBoxScrap = routes;

    gmaps = googlemaps.Client("AIzaSyAB_QsjZviwHVJHyBCeTPiK8M1NOvSLcns");
    # calc distance
    for i in range(0, len(busstops)):
        parsedData[list(busstops.keys())[i]] = []
        for l, stop in busstops[list(busstops.keys())[i]].iterrows():
            parsedData[list(busstops.keys())[i]].append(
                {
                    "Name": stop["Bus stop"],
                    "GPS Location": stop["GPS Location"]
                }
            )
            graphedData[stop["Bus stop"]] = []
        key = list(parsedData.keys())[i]
        prevSave = 0
        for dataIndex in range(0, len(parsedData[key])):
            returnIndex = 0
            check = 5000
            point = None
            counter = 0
            for coordinates in range(prevSave, len(mapBoxScrap[list(mapBoxScrap.keys())[i]])):
                counter +=1
                if(counter == 51):
                    break
                busStop = parsedData[key][dataIndex]
                distance = calcdistance(
                    (float(busStop["GPS Location"].split(",")[0].strip()),
                     float(busStop["GPS Location"].split(",")[1].strip())),
                    (float(mapBoxScrap[list(mapBoxScrap.keys())[i]][coordinates][1]),
                     float(mapBoxScrap[list(mapBoxScrap.keys())[i]][coordinates][0])))
                if distance < check:
                    check = distance
                    point = mapBoxScrap[list(mapBoxScrap.keys())[i]][coordinates]
                    returnIndex = coordinates
                    prevSave = coordinates
            parsedData[key][dataIndex]['Distance Away'] = check
            parsedData[key][dataIndex]["Closest Point"] = point
            parsedData[key][dataIndex]["Index in route[]"] = returnIndex
        busServiceForRoute = list(mapBoxScrap.keys())[i]
        routeCounter = 0
        for dataIndex in range(0, len(parsedData[key])-1):
            counterDist = 0
            for routeIndexIterator in range(routeCounter, len(mapBoxScrap[busServiceForRoute]) - 1):
                origin = (mapBoxScrap[busServiceForRoute][routeIndexIterator][1],
                          mapBoxScrap[busServiceForRoute][routeIndexIterator][0])
                destination = (
                    mapBoxScrap[busServiceForRoute][routeIndexIterator + 1][1],
                    mapBoxScrap[busServiceForRoute][routeIndexIterator + 1][0])
                # temp = gmaps.distance_matrix(origin, destination, mode="driving")["rows"][0]["elements"][0][

                #    "distance"][
                #   "value"]
                temp = calcdistance(origin, destination)
                counterDist += temp

                if parsedData[key][dataIndex + 1]["Closest Point"] == mapBoxScrap[busServiceForRoute][
                    routeIndexIterator +1]:
                    parsedData[key][dataIndex]["Distance to Next"] = counterDist
                    routeCounter = routeIndexIterator
                    break
                routeCounter = routeIndexIterator
    for stopName in graphedData.keys():
        graphedData[stopName].append({"Buses Supported": []})
        for i in parsedData.keys():
            for d in range(0, len(parsedData[i]) - 1):
                if stopName == parsedData[i][d]["Name"]:
                    graphedData[stopName][0]["Buses Supported"].append(i)
                    try:
                        graphedData[stopName].append({
                            "Name": parsedData[i][d + 1]["Name"],
                            "Bus": i,
                            "Distance Away": float(parsedData[i][d]["Distance to Next"])
                        })
                    except KeyError:
                        graphedData[stopName].append({
                            "Name": parsedData[i][d + 1]["Name"],
                            "Bus": i,
                            "Distance Away": "Issue"
                        })

                    break
        graphedData[stopName][0]["Buses Supported"] = list(set(graphedData[stopName][0]["Buses Supported"]))


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
            temp = calcdistance(place, [stop["Closest Point"][1], stop["Closest Point"][0]])
            if temp <= distanceAway:
                distanceAway = temp
                busToTake = i
                busStopToTake = stop["Name"]
    print("Bus to Take: " + busToTake + " going towards " + parsedData[busToTake][-1]["Name"])
    print("Bus Stop to Take: " + busStopToTake)
'''
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


# def transfer(distancealrtravelled):


startLoc = [1.4689940555974177, 103.7368740086021]
endLoc = [1.4635691591027955, 103.76499694129318]
preprocessing()
print(graphedData["Taman Universiti Terminal"])
dijkstras.Dijkstras(graphedData, "Larkin Terminal", "Taman Universiti Terminal")
print()

#calcBusToTake([1.4794125239358897, 103.72578357602447])

# giveRoute(startLoc, endLoc)
