class BusGraph:

    def __init__(self, bus_dict=None, directed=True):
        self.bus_dict = bus_dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()

    # Create an undirected graph by adding symmetric edges
    def make_undirected(self):
        for a in list(self.bus_dict.keys()):
            for(b, dist) in self.bus_dict[a].items():
                self.bus_dict.setdefault(b, {})[a] = dict

    # Add a link from A and B of given distance, and also add the inverse link if the graph is undirected
    def connect(self, A, B, distance=1):
        self.bus_dict.setdefault(A,{})[B] = distance
        if not self.directed:
            self.bus_dict.setdefault(B, {})[A] = distance

    # Get neighbors or a neighbor
    def getNeighbor(self, a, b=None):
        links = self.bus_dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.getNeighbor(b)

    # Return a list of nodes in the graph
    def nodes(self):
        s1 = set([k for k in self.bus_dict.keys()])
        s2 = set([k2 for v in self.bus_dict.values() for k2,v2 in v.items()])
        nodes = s1.union(s2)
        return list(nodes)


class Node:
    def __init__(self, stopname: str, parent:str):
        self.stopname = stopname
        self.parent = parent
        self.startDist = 0
        self.endDist = 0
        self.totalCost = 0

    def __eq__(self, other):
        return self.stopname == other.stopname

    # Sort nodes
    def __lt__(self, other):
        return self.totalCost < other.totalCost

    # Print Node
    def __repr__(self):
        return ('({0}, {1})'.format(self.stopname, self.totalCost))


def AStarAlgo(busGraph, heuristics, start, end):
    # List for open and close nodes
    open = []
    closed = []

    startNode = Node(start, None)
    endNode = Node(end, None)

    open.append(startNode)

    while len(open) > 0:
        open.sort()

        # Get the node with the lowest cost
        currentNode = open.pop(0)

        # Add the current node to the closed list
        closed.append(endNode)

        if currentNode == endNode:
            path = []
            while currentNode != startNode:
                path.append(currentNode.stopname + ': ' + str(currentNode.startDist))
                # Return reversed path
                return path[::-1]
        neighbors = busGraph.get(currentNode.stopname)

        for key, value in neighbors.items():
            # Create neighbor node
            neighbor = Node(key, currentNode)

            # Check if neighbor in closed list
            if (neighbor in closed):
                continue

            # Calculate full path cost
            neighbor.startDist = currentNode.startDist + busGraph.get(currentNode.name, neighbor.name)
            neighbor.endDist = heuristics.get(neighbor.stopname)
            neighbor.totalCost = neighbor.startDist + neighbor.endDist

            # Check if the neighbor is in open list and have lower total Cost value
            if (add_to_open(open, neighbor) == True):
                open.append(neighbor)
    # No path is found
    return None


def add_to_open(open, neighbor):
    for node in open:
        if (neighbor == node and neighbor.totalCost > node.totalCost):
            return False
    return True







        


