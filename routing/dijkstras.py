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

        toReturn = {"Transfers": []}
        pathing = [end]
        nextBusStop = self.prev[end]
        walkingXfer = False
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
                if busTaking == None:
                    busTaking = set(self.graph[nextBusStop][0]["Buses Supported"]) & set(
                        self.graph[currentBusStop][0]["Buses Supported"])

                for i in self.graph[currentBusStop][2]["Stops Nearby"]:
                    if self.distance[currentBusStop] > self.distance[i]:
                        nextBusStop = i
                        # print("current distance from: " + currentBusStop + " to" + start + " is : " + str(
                            self.distance[currentBusStop]))
                        # print("current distance from: " + i + " to" + start + " is : " + str(self.distance[i]))
                        # print("Detected nearer bus stop")
                        # print(self.distance[i])
                        walkingXfer = True

                if len(nextBusStop) != 0 and \
                        bool(set(busTaking).isdisjoint(set(self.graph[currentBusStop][0]["Buses Supported"]) & \
                                                       set(self.graph[nextBusStop][0]["Buses Supported"]))):
                    if transferCount != 0:
                        toReturn["Transfers"][transferCount - 1]["Transfer To"] = list(busTaking)[0]
                    # Transfer detected in path
                    if walkingXfer:
                        toReturn["Transfers"].append({
                            "TransferStop": currentBusStop,
                            "TransferTOSTOP": nextBusStop,
                            "Transfer From": list(busTaking)[0],
                            "Transfer To": ""
                        })
                        walkingXfer = False;
                    else:
                        toReturn["Transfers"].append({
                            "TransferStop": currentBusStop,
                            "Transfer From": list(busTaking)[0],
                            "Transfer To": ""
                        })
                    busTaking = set(self.graph[currentBusStop][0]["Buses Supported"]) & set(
                        self.graph[nextBusStop][0]["Buses Supported"])

                    transferCount += 1

                if len(nextBusStop) == 0:
                    if (len(toReturn["Transfers"]) == 0):
                        toReturn["Transfers"].append({
                            "TransferStop": end,
                            "Transfer From": list(busTaking)[0],
                            "Transfer To": list(busTaking)[0],
                        })
                    else:
                        toReturn["Transfers"][transferCount - 1]["Transfer To"] = list(busTaking)[0]
                    break
                busTaking = busTaking & set(self.graph[nextBusStop][0]["Buses Supported"])
        print(pathing)
        print(toReturn)
        toReturn["Distance"] = self.distance[end]
        self.toReturn = toReturn
        return toReturn
