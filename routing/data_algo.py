import pickle
import googlemaps
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime

from routes_reader.routes_reader import RoutesReader
routes_reader = RoutesReader()

busstops = routes_reader.read_excel('bus_stops.xlsx')
P101BusStops = busstops["P101-loop"]


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
        print(routes)
        gmaps = googlemaps.Client("AIzaSyAB_QsjZviwHVJHyBCeTPiK8M1NOvSLcns");
        # calc distance
        for i in range(0, len(busstops)):
            busstops[list(busstops.keys())[i]]["Distance Away"] = ""
            busstops[list(busstops.keys())[i]]["Closest Point"] = ""
            busstops[list(busstops.keys())[i]]["DistanceToNext"] = ""
            busstops[list(busstops.keys())[i]]["Next Point"] = busstops[list(busstops.keys())[i]]["Closest Point"].shift(+1)

            for l, stop in busstops[list(busstops.keys())[i]].iterrows():
                check = 5000;
                point = None
                for coordinates in routes[list(routes.keys())[i]]:
                    try:
                        distance = calcdistance(
                            (float(stop["GPS Location"].split(",")[0].strip()),
                             float(stop["GPS Location"].split(",")[1].strip())),
                            (coordinates[1], coordinates[0]))
                        if distance < check:
                            check = distance
                            point = coordinates
                    except ValueError:
                        print("Just catching")
                busstops[list(busstops.keys())[i]].at[l, 'Distance Away'] = check
                busstops[list(busstops.keys())[i]].at[l, 'Closest Point'] = str(point)
        totalDistance = 0
        counterDist = 0
        counter = 0
        for i in range(0, len(busstops)):
            for l, stop in busstops[list(busstops.keys())[i]].iterrows():
                for d in range(0, len(routes[list(routes.keys())[i]]) - 2):
                    counter +=1
                    #origin = (routes[list(routes.keys())[i]][d][1], routes[list(routes.keys())[i]][d][0])
                    #destination = (
                    #    routes[list(routes.keys())[i]][d + 1][1], routes[list(routes.keys())[i]][d + 1][0])
                    #temp = gmaps.distance_matrix(origin, destination, mode="driving")["rows"][0]["elements"][0][
                    #    "distance"][
                    #   "value"]
                    #counterDist += temp
                    #totalDistance += temp
                    #if stop['Next Point'] == routes[list(routes.keys())[i]][d + 1]:
                    #    print("Found")
                    #    busstops[list(busstops.keys())[i]].at[l, 'DistanceToNext'] = counterDist
                    #    counterDist = 0
        print(counter)


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


def giveRoute(fromHere, toHere):
    with open('../routes_scraper/routes.bin', 'rb') as f:
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
        for i in routes["P101_1"][routes["P101_1"].index(startingBusStop["Closest Point"]):routes["P101_1"].index(endingBusStop["Closest Point"])+1]:
            listOfReturnRoute.append(i)

        toReturn = {
            "Starting Bus Stop": startingBusStop,
            "Ending Bus Stop":endingBusStop,
            "Route Taken": listOfReturnRoute,
            "Distance Travelled":distance,
            "Distance Travelled (KM)": distance/1000,
            "Time Taken": timetaken
        }
        return toReturn
#def transfer(distancealrtravelled):


startLoc = [1.4689940555974177, 103.7368740086021]
endLoc = [1.4635691591027955, 103.76499694129318]
preprocessing()
for l, r in busstops["P101-loop"].iterrows():
    print(r)
#giveRoute(startLoc, endLoc)





