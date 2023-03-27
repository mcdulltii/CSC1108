import sys


class Dijkstras:
    startingForToReturn = None
    toReturn = None
    graph = None
    distance = {}
    prev = {}

    def __init__(self, graph):
        self.graph = graph

    def calculate_route(self, end: str, start: str):
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
                for i in range(3, len(self.graph[v])):
                    # list of verticles connected to v
                    if self.graph[v][i]["Name"] in q:
                        alt = self.distance[v] + self.graph[v][i]["Distance Away"]
                        if alt < self.distance[self.graph[v][i]["Name"]]:
                            self.distance[self.graph[v][i]["Name"]] = alt
                            self.prev[self.graph[v][i]["Name"]] = v
        # print(self.prev)
        toReturn = {"Transfers": []}
        pathing = [end]
        nextBusStop = end
        walkingXfer = False
        # take note of crossing over
        busTaking = None
        busesToReturn = []
        transfers = []
        walkingTransfer = False;
        distanceToReturn = self.distance[end]
        while nextBusStop != start:
            currentBusStop = nextBusStop
            nextBusStop = self.prev[currentBusStop]
            for closeBusStop in self.graph[currentBusStop][2]["Stops Nearby"]:
                if self.distance[closeBusStop]<self.distance[currentBusStop] and closeBusStop != nextBusStop:
                    nextBusStop = closeBusStop
                    walkingTransfer = True
            if busTaking is None:
                busTaking = set(self.graph[currentBusStop][0]["Buses Supported"])
            if busTaking.isdisjoint(set(self.graph[nextBusStop][0]["Buses Supported"])):
                busesToReturn.append(list(busTaking))
                if walkingTransfer:
                    transfers.append({"Transfer Stop From": currentBusStop,"Transfer Stop To": nextBusStop, "Type": "Walking"})
                    distanceToReturn -= self.distance[currentBusStop]
                    distanceToReturn += self.distance[nextBusStop]
                else:
                    transfers.append({"Transfer Stop": currentBusStop, "Type": "On-Site"})
                busTaking = set(self.graph[nextBusStop][0]["Buses Supported"])
            else:
                busTaking = set(self.graph[nextBusStop][0]["Buses Supported"]) & set(busTaking)
            pathing.append(nextBusStop)
            walkingTransfer = False
            if nextBusStop == start:
                busesToReturn.append(list(busTaking))
        # print(pathing)
        # print(busesToReturn)
        # print(transfers)
        toReturn = {"Pathing": pathing, "Buses To Return": busesToReturn, "Transfers": transfers,
                    "Distance": distanceToReturn}
        # print(toReturn)
        self.toReturn = toReturn
        return toReturn
