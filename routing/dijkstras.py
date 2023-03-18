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

    def __init__(self, graph):
        self.graph = graph

    def calculateRoute(self, start, end):
        if self.startingForToReturn != start:
            self.startingForToReturn = start
            q = []
            for i in self.graph:
                self.prev[i] = []
                self.distance[i] = sys.maxsize
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
        toReturn = {"Transfers": []}
        nextBusStop = end
        pathing = []
        # take note of crossing over
        while nextBusStop:
            # Logic for catch xfer is here
            # prev current next to get xfer details
            pathing.append(nextBusStop)
            if pathing[pathing.index(nextBusStop) - 1]:
                previousBusStop = pathing[pathing.index(nextBusStop) - 1]
                currentBusStop = nextBusStop
                nextBusStop = self.prev[nextBusStop]

                if len(nextBusStop) != 0 and bool(set(self.graph[previousBusStop][0]["Buses Supported"]).isdisjoint(
                        self.graph[nextBusStop][0]["Buses Supported"])):
                    toReturn["Transfers"].append({
                        "TransferStop": currentBusStop,
                        "TransferStopBuses": self.graph[currentBusStop][0]["Buses Supported"],
                        "Transfer From": self.graph[nextBusStop][0]["Buses Supported"],
                        "Transfer To": self.graph[previousBusStop][0]["Buses Supported"]
                    })

        toReturn["Distance"] = self.distance[end]
        self.toReturn = toReturn
        return toReturn
