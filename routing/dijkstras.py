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
                for i in range(3, len(self.graph[v])):
                    # list of verticles connected to v
                    if self.graph[v][i]["Name"] in q:
                        alt = self.distance[v] + self.graph[v][i]["Distance Away"]
                        if alt < self.distance[self.graph[v][i]["Name"]]:
                            self.distance[self.graph[v][i]["Name"]] = alt
                            self.prev[self.graph[v][i]["Name"]] = v
                            self.test[self.graph[v][i]["Name"]].append(self.distance[v])
                            self.test[self.graph[v][i]["Name"]].append(self.graph[v][i]["Distance Away"])

        toReturn = {"Transfers": []}
        pathing = [end]
        nextBusStop = self.prev[end]
        # take note of crossing over
        busTaking = None
        transferCount = 0
        while nextBusStop:
            # Logic for catch xfer is here
            # prev current next to get xfer details
            pathing.append(nextBusStop)
            if pathing[pathing.index(nextBusStop) - 1]:
                previousBusStop = pathing[pathing.index(nextBusStop) - 1]
                currentBusStop = nextBusStop
                nextBusStop = self.prev[nextBusStop]
                if (busTaking == None):
                    busTaking = set(self.graph[nextBusStop][0]["Buses Supported"]) & set(
                        self.graph[currentBusStop][0]["Buses Supported"])

                """for i in self.graph[currentBusStop][2]["Stops Nearby"]:
                    print("current distance from: " + currentBusStop + " to" + start + " is : " + str(
                        self.distance[currentBusStop]))
                    print("current distance from: " + i + " to" + start + " is : " + str(self.distance[i]))

                    if self.distance[currentBusStop] > self.distance[i]:
                        print("Detected nearer bus stop")
                        print(self.distance[i])"""
                if len(nextBusStop) != 0 and \
                        bool(set(busTaking).isdisjoint(set(self.graph[currentBusStop][0]["Buses Supported"]) & set(
                        self.graph[nextBusStop][0]["Buses Supported"]))):
                    # transfer detected in path
                    toReturn["Transfers"].append({
                        "TransferStop": currentBusStop,
                        "Transfer From": list(busTaking)[0],
                        "Transfer To": ""
                    })
                    busTaking = set(self.graph[currentBusStop][0]["Buses Supported"]) & set(
                    self.graph[nextBusStop][0]["Buses Supported"])

                    transferCount += 1
                    if(transferCount != 1):
                        toReturn["Transfers"][transferCount - 1]["Transfer To"] = list(busTaking)[0]
                if len(nextBusStop) == 0:
                    toReturn["Transfers"][transferCount - 1]["Transfer To"] = list(busTaking)[0]
                    break
                busTaking = busTaking & set(
                    self.graph[nextBusStop][0]["Buses Supported"])

        toReturn["Distance"] = self.distance[end]
        print(toReturn)
        self.toReturn = toReturn
        return toReturn
