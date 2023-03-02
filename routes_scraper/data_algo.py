import pickle
import googlemaps;
from math import sin, cos, sqrt, atan2, radians
def calcdistance(coordinate1, coordinate2):
    R = 6373.0 #earth
    lat1 = radians(coordinate1[0])
    lon1 = radians(coordinate1[1])
    lat2 = radians(coordinate2[0])
    lon2= radians(coordinate2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1;

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

with open('routes.txt','rb') as f:
    routes = pickle.load(f)
    #routes["P101_1"] = routes["P101_1"][0:100]
    gmaps = googlemaps.Client("AIzaSyAB_QsjZviwHVJHyBCeTPiK8M1NOvSLcns");
    distance = 0
    P101BusStops = [
        {'Name': 'Larkin Terminal', 'Coordinates': (1.4964559999542668, 103.74374661113058), 'Distance Away': 0.13276671286930164, 'Closest Point': [103.74319, 1.4954], 'DistanceToNext': 25},
        {'Name': 'Pejabat Daerah Tanah Johor Bahru', 'Coordinates': (1.491850778809332, 103.74087255093272), 'Distance Away': 0.022623988236764085, 'Closest Point': [103.74084, 1.49165], 'DistanceToNext': 649},
        {'Name': 'RTM Jabatan Penyiaran Negeri Johor', 'Coordinates': (1.4801823177394162, 103.7368168221016), 'Distance Away': 0.027262168785975253, 'Closest Point': [103.73678, 1.47994], 'DistanceToNext': 1402},
        {'Name': 'Opp Masjid Kolam Ayer', 'Coordinates': (1.4689940555974177, 103.7368740086021), 'Distance Away': 0.01808383743834511, 'Closest Point': [103.73676, 1.46911], 'DistanceToNext': 1225},
        {'Name': 'Opp Jabatan Pendidikan Johor', 'Coordinates': (1.4675510557185905, 103.73673088953657), 'Distance Away': 0.009944986733478973, 'Closest Point': [103.73674, 1.46764], 'DistanceToNext': 165},
        {'Name': 'Maktab Sultan Abu Bakar (English College', 'Coordinates': (1.4627466510403129, 103.73965194475493), 'Distance Away': 0.031420748022062045, 'Closest Point': [103.73977, 1.46249], 'DistanceToNext': 717},
        {'Name': 'Hospital Sultanah Aminah', 'Coordinates': (1.4575742843315376, 103.74670675307506), 'Distance Away': 0.021653067738086933, 'Closest Point': [103.74662, 1.4574], 'DistanceToNext': 1268},
        {'Name': 'Johor Islamic Complex', 'Coordinates': (1.456742090233385, 103.74938268472616), 'Distance Away': 0.017103988838286607, 'Closest Point': [103.74936, 1.45659], 'DistanceToNext': 317},
        {'Name': 'Bangunan Sultan Ibrahim', 'Coordinates': (1.4598336266506124, 103.76216068221784), 'Distance Away': 0.010664978489722256, 'Closest Point': [103.76214, 1.45974], 'DistanceToNext': 3580},
        {'Name': 'Wisma Persekutuan', 'Coordinates': (1.4609620562865593, 103.75782511045665), 'Distance Away': 0.026116184037687448, 'Closest Point': [103.75769, 1.46077], 'DistanceToNext': 1904},
        {'Name': 'Majlis Bandaraya Johor Bahru', 'Coordinates': (1.4555985388016415, 103.76176881099856), 'Distance Away': 0.029079238395833085, 'Closest Point': [103.76173, 1.45534], 'DistanceToNext': 946},
        {'Name': 'JB Sentral Terminal', 'Coordinates': (1.4635691591027955, 103.76499694129318), 'Distance Away': 0.018011762789580922, 'Closest Point': [103.76506, 1.46342], 'DistanceToNext': 1309},
        {'Name': 'Menara MSC Cyberport', 'Coordinates': (1.4622515143439279, 103.77198033612271), 'Distance Away': 0.014600639242670495, 'Closest Point': [103.77203, 1.46213], 'DistanceToNext': 19122},
        {'Name': 'Opp Sekolah Kebangsaan Perempuan Jalan Yahya Awal', 'Coordinates': (1.4728712972429236, 103.74885185047674), 'Distance Away': 0.017707754609470664, 'Closest Point': [103.74901, 1.47289], 'DistanceToNext': 3742},
        {'Name': 'Petronas Kiosk @ Jalan Yahya Awal', 'Coordinates': (1.4753718119884702, 103.7479248341084), 'Distance Away': 0.023499810226244533, 'Closest Point': [103.74809, 1.47524], 'DistanceToNext': 2092},
        {'Name': 'Opp SJK (T) Jalan Yahya Awal', 'Coordinates': (1.478736856876273, 103.74753116069688), 'Distance Away': 0.034535070995482024, 'Closest Point': [103.74765, 1.47845], 'DistanceToNext': 4753},
        {'Name': 'aft Jalan Tasek Utara', 'Coordinates': (1.4810361535128787, 103.74738498637815), 'Distance Away': 0.020758442753045992, 'Closest Point': [103.74747, 1.48087], 'DistanceToNext': 1378},
        {'Name': 'Opp Yayasan Bandaraya Johor Bahru', 'Coordinates': (1.4843491421227393, 103.74925303801986), 'Distance Away': 0.021676605767557346, 'Closest Point': [103.7493, 1.48416], 'DistanceToNext': 13595},
        {'Name': 'Larkin Terminal', 'Coordinates': (1.4964559999542668, 103.74374661113058), 'Distance Away': 0.13276671286930164, 'Closest Point': [103.74319, 1.4954]}
    ]


    busstopcounter = 1;
    distancetobusstop = 500000000;
    distancetrack=0
    #calc distance
    for i in P101BusStops:
        check = 5000;
        point = None
        for d in routes["P101_1"]:
            distance = calcdistance(i["Coordinates"], (d[1], d[0]))
            if(distance < check):
                check = distance
                point = d
        i["Distance Away"] = check
        i["Closest Point"] = point


    counter = 0
    counterDist = 0
    totalDistance = 0

    for i in range(0,len(routes["P101_1"])-2):
        origin = (routes["P101_1"][i][1], routes["P101_1"][i][0])
        destination = (routes["P101_1"][i+1][1], routes["P101_1"][i+1][0])
        temp = gmaps.distance_matrix(origin, destination, mode="driving")["rows"][0]["elements"][0]["distance"]["value"]
        counterDist += temp
        totalDistance += temp
        if counter >= len(P101BusStops):
            continue
        if P101BusStops[counter+1]['Closest Point'] == routes["P101_1"][i+1]:
            print("Found")
            P101BusStops[counter]["DistanceToNext"] = counterDist
            counter +=1
            counterDist = 0
            print(P101BusStops)
    print(distance)
    print(P101BusStops)

    startLoc = [101.74325, 1.49519]
    endLoc = [103.64737, 1.61245]


