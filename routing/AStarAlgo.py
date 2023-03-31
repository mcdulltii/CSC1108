from queue import PriorityQueue
from math import sin, cos, sqrt, atan2, radians

from routing import data_algo


class AStar:
    graph = None
    forBusTransferFunction = None

    def __init__(self, graph):
        self.graph = graph

    def calculate_route(self, start, end):
        route = {"NodesVisited": [], "Transfers": [], "Distance": 0, "Path": []}

        if start not in self.graph or end not in self.graph:
            print("Start or end node not in graph")
            return route

        # Priority queue with f(n) = g(n) + h(n)
        q = PriorityQueue()
        # Stores the current shortest distance from the starting node to each node
        g = {start: 0}
        # Stores the estimated shortest distance from each node to the end node
        h = {start: self.heuristic(start, end)}
        # Stores the node that was used to reach the current node with the shortest distance
        prev = {}

        q.put((g[start] + h[start], start))

        while not q.empty():
            print("q", q.queue)
            node = q.get()[1]
            print("Visiting node", node)
            route["NodesVisited"].append(node)

            if node == end:
                route["Distance"] = g[end]
                route["Transfers"] = self.get_transfers(start, end, prev)
                break

            for i in range(3, len(self.graph[node])):
                neighbor = self.graph[node][i]
                print("Exploring neighbor", neighbor)
                neighborName = neighbor["Name"]
                if neighborName not in g:
                    g[neighborName] = float("inf")
                weight = neighbor["Distance Away"]
                transfer = self.check(neighborName)
                transferTime = 0
                if transfer:
                    transferTime = 15
                if g[node] + weight + transferTime < g[neighborName]:
                    g[neighborName] = g[node] + weight + transferTime
                    h[neighborName] = neighbor["Distance Away"]
                    prev[neighborName] = node
                    q.put((g[neighborName] + h[neighborName], neighborName))
        print("prev", prev)
        if route["Distance"] == 0:
            route["Distance"] = None
        path = [end]
        current_node = end
        while current_node != start:
            current_node = prev[current_node]
            path.append(current_node)
        path.reverse()

        route["Path"] = path

        return route

    def heuristic(self, node, end):
        """
        Calculate the heuristic (estimated shortest distance) between node and end
        """
        lat1, lon1 = self.graph[node][1]['Close Point'][0]
        lat2, lon2 = self.graph[end][1]['Close Point'][0]
        # approximate radius of earth in km
        R = 6373.0
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance

    def get_transfers(self, start, end, prev):
        """
        Get the transfers needed to reach end from start using prev
        """
        transfers = []
        current_node = end
        if current_node not in prev:
            print("No route found")
            return transfers
        while current_node != start:
            transfer_from = prev[current_node]
            transfer_to = current_node
            current_node = transfer_from
            # Check if the route has already been added to transfers
            for t in transfers:
                if t["Bus"] == self.graph[transfer_from][0] and t["Transfer From"] == transfer_from:
                    t["Transfer To"] = transfer_to
                    break
            else:
                transfers.append({"Bus": self.graph[transfer_from][0], "Transfer From": transfer_from, "Transfer To": transfer_to})
        transfers.reverse()
        return transfers

    def check(self, currentBusStop):
        if self.forBusTransferFunction == None:
            self.forBusTransferFunction = set(self.graph[currentBusStop][0]["Buses Supported"])
            return False
        else:
            if self.forBusTransferFunction.isdisjoint(set(self.graph[currentBusStop][0]["Buses Supported"])):
                self.forBusTransferFunction = set(self.graph[currentBusStop][0]["Buses Supported"])
                return True
            else:
                self.forBusTransferFunction = set(self.graph[currentBusStop][0]["Buses Supported"])
                return False


# Testing
dataobj = data_algo.RoutingAlgo()
graph = dataobj.graphedData
print(graph)
aSTar = AStar(graph)
route = aSTar.calculate_route("Majlis Bandaraya Johor Bahru", "AEON Tebrau City")

if route["Distance"] is None:
    print("No route found!")
else:
    print(f"Distance: {route['Distance']:.2f} km")
    print("Nodes visited: ", route["NodesVisited"])
    print("Transfers: ")
    for t in route["Transfers"]:
        print(f"Take bus {t['Bus']} from {t['Transfer From']} to {t['Transfer To']}")