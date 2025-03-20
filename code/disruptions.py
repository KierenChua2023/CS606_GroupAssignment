"""
This handle possible disruptions for the day
"""
from rcjsp import Attraction, Tourist
from typing import List

def rainy_day_attraction(attraction_list : List[Attraction], day : int) -> List[Attraction]:
    """
    Rainy Day, all outdoor, nature and Sporty activities are no longer 
    available for the day
    """
    print("Rainy Day")
    new_attraction_list = []
    for attraction in attraction_list:
        if "Sporty" in attraction.categories or \
            "Nature" in attraction.categories or \
            "Outdoor" in attraction.categories:
            # Amend all the attraction opening hours for today
            del attraction.opening_hours[day]
        new_attraction_list.append(attraction)

    return new_attraction_list

def sick_day_attraction(attraction_list : List[Attraction], day : int):
    """
    Your plans for the day is wiped out, all attractions would be closed to you
    for the day
    """
    print("Sick Day")
    new_attraction_list = []
    for attraction in attraction_list:
        # Amend all the attraction opening hours for today
        del attraction.opening_hours[day]
        new_attraction_list.append(attraction)

    return new_attraction_list

def nothing_happens_attraction(attraction_list : List[Attraction], day : int):
    """
    Nothing happens, everything is normal
    """
    return attraction_list
