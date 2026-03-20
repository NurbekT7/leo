import math


def is_near_school(user_lat, user_lon):
    SCHOOL_LAT = 42.86184306352933
    SCHOOL_LON = 74.47734210521938

    R = 6371
    dlat = math.radians(user_lat - SCHOOL_LAT)
    dlon = math.radians(user_lon - SCHOOL_LON)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(SCHOOL_LAT)) * math.cos(math.radians(user_lat)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance <= 4.0