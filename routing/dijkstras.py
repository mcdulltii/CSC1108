import math
import queue
import sys

from heap import Heap, printArr


class Dijkstras:
    toReturn = None
    graph = None
    startingForToReturn = None
    prev = {}
    distance = {}
    test = {}

    def __init__(self, graph):
        self.graph = graph

    def calculateRoute(self, end, start):
        if self.startingForToReturn != start:
            self.startingForToReturn = start
            q = []
            for i in self.graph:
                self.prev[i] = []
                self.distance[i] = sys.maxsize
                self.test[i] = []
                q.append(i)
            self.distance[self.startingForToReturn] = 0
            while len(q) != 0:
                v = min(q, key=self.distance.get)
                q.remove(v)
                for i in range(1, len(self.graph[v])):
                    # list of verticles connected to v
                    if self.graph[v][i]["Name"] in q:
                        alt = self.distance[v] + self.graph[v][i]["Distance Away"]
                        if alt < self.distance[self.graph[v][i]["Name"]]:
                            self.distance[self.graph[v][i]["Name"]] = alt
                            self.prev[self.graph[v][i]["Name"]] = v
                            self.test[self.graph[v][i]["Name"]].append(self.distance[v])
                            self.test[self.graph[v][i]["Name"]].append(self.graph[v][i]["Distance Away"])

        toReturn = {"Transfers": []}
        print(self.distance)
        pathing = [end]
        nextBusStop = self.prev[end]
        print(self.test)
        # take note of crossing over
        while nextBusStop:
            # Logic for catch xfer is here
            # prev current next to get xfer details
            pathing.append(nextBusStop)
            if pathing[pathing.index(nextBusStop) - 1]:
                previousBusStop = pathing[pathing.index(nextBusStop) - 1]
                currentBusStop = nextBusStop
                nextBusStop = self.prev[nextBusStop]
                if currentBusStop != start and len(nextBusStop) != 0 and \
                        bool(set(self.graph[previousBusStop][0]["Buses Supported"]).isdisjoint(
                            self.graph[nextBusStop][0]["Buses Supported"])):
                    toReturn["Transfers"].append({
                        "TransferStop": currentBusStop,
                        "Transfer From": "",
                        "Transfer To": ""
                    })
        toReturn["Distance"] = self.distance[end]
        toReturn["Transfers"].reverse()

        counter = 0
        checkBusStop = self.graph[end][0]["Buses Supported"]

        busesTaken = []
        for i in range(1, len(pathing)):
            checkBusStop = set(checkBusStop) & set(self.graph[pathing[i]][0]["Buses Supported"])
            if pathing[i] == toReturn["Transfers"][counter]["TransferStop"] or i == len(pathing) - 1:
                busesTaken.append(checkBusStop)
                if counter + 1 < len(toReturn["Transfers"]):
                    counter += 1
                checkBusStop = self.graph[toReturn["Transfers"][counter]["TransferStop"]][0]["Buses Supported"]
        print(busesTaken)
        for i in range(0, len(busesTaken) - 1):
            toReturn["Transfers"][i]["Transfer From"] = list(busesTaken[i])[0]
            toReturn["Transfers"][i]["Transfer To"] = list(busesTaken[i + 1])[0]

        self.toReturn = toReturn
        return toReturn
