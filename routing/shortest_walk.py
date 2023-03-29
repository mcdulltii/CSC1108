import googlemaps

from math import radians, cos, sin, asin, sqrt
from routes_reader.routes_reader import RoutesReader


class shortest_walk:

    def __init__(self, bus_stops):
        # bus stop coordinates
        # format: { {'P101': {'Name': 'Larkin Terminal ⊃ Johor Bahru City (loop service)', 'Coordinates': '41.40338, 2.17403'} }
        self.list_of_bus_stops = bus_stops

    # googlemaps api key
    gmaps = googlemaps.Client(key='AIzaSyAB_QsjZviwHVJHyBCeTPiK8M1NOvSLcns')

    '''
    # converting user address to location as coordinates
    # user address would be the location name, not coordinates
    user_geocode_result = gmaps.geocode(user_loc)
    user_lat = user_geocode_result[0]['geometry']['location']['lat']
    user_lon = user_geocode_result[0]['geometry']['location']['lng']
    '''

    # haversine formula (kilometers): calculates distance between 2 points on a sphere, given longitude and latitude
    # coordinates: 1 = user location, 2 = destination location
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        # convert decimal degrees to radians
        # needs to be in radians to pass trigonometric functions
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # radius of the earth
        R = 6371

        # delta values
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        # haversine formula
        a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        c = 2 * asin(sqrt(a))
        dist = c * R

        return dist

    def string_to_coordinate(self, location_in_string):
        print(location_in_string)
        google_return = self.gmaps.geocode(location_in_string)
        print(google_return)

        to_return = [google_return[0]['geometry']['location'] ['lat'], google_return[0]['geometry']['location'] ['lng']]
        return to_return

    # locate nearest bus stop
    def get_walking_route(self,locationStart, locationEnd):
        directions_result = self.gmaps.directions(locationStart, locationEnd, mode="walking")
        route_coordinates = [(step['start_location']['lng'], step['start_location']['lat'])
                             for step in directions_result[0]['legs'][0]['steps']]
        return route_coordinates

    def find_nearby(self, location):
        # set the search radius
        max_distance = 30
        closest_stop = (0, 0)
        nearby = {}
        user_lat = location[0]
        user_lon = location[1]

        # iterate through bus stops
        for key in self.list_of_bus_stops:
            for bus_stop in self.list_of_bus_stops[key]:

                # split each bus stop coordinate into both latitude and longitude
                coords = bus_stop['GPS Location'].split(", ")

                coord_lat = float(coords[0])
                coord_lon = float(coords[1])
                print(location)
                print(coords)
                distance = self.haversine_distance(user_lat, user_lon, coord_lat, coord_lon)
                print(distance)
                if distance <= max_distance:
                    if key in nearby.keys():

                        # 1 bus service, 1 nearest bus stop from point
                        if nearby[key]["Distance From Point"] > distance:
                            bus_stop["Distance From Point"] = distance
                            nearby[key] = bus_stop
                    else:
                        bus_stop["Distance From Point"] = distance
                        nearby[key] = bus_stop

        # starting range, for distance away from point
        # find the nearest bus stop among all the range

        distance_away_from = 40
        closest_stop = None

        for keys in nearby:
            if distance_away_from > nearby[keys]["Distance From Point"]:
                distance_away_from = nearby[keys]["Distance From Point"]
                closest_stop = nearby[keys]
                
        if closest_stop is not None:
            print("HA FOUND CLOSE")
            directions_result = self.gmaps.directions(location, closest_stop["GPS Location"], mode="walking")
            route_coordinates = [(step['start_location']['lng'], step['start_location']['lat'])
                                 for step in directions_result[0]['legs'][0]['steps']]
        else:
            route_coordinates = None

        return [route_coordinates, closest_stop]
