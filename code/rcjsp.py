import copy
import json
import random
import csv
import ast

from src.alns import State
from typing import List


class Attraction(object):
    def __init__(self, attraction_data : list, idx : int):
        self.type_list = ["Cultural",
                          "Sporty",
                          "Nature",
                          "Family",
                          "Shopping",
                          "Culinary",
                          "Outdoor"]

        self.idx = idx
        self.attraction_name = attraction_data[0]
        self.lat_long = [float(attraction_data[1]), float(attraction_data[2])]
        self.task_time = float(attraction_data[3])
        self.opening_hours = ast.literal_eval(attraction_data[4])

        # Adjust opening hours to check for formatting
        for key in self.opening_hours.keys():
            hours = self.opening_hours[key]
            new_hours = []
            if int(hours[0]) != float(hours[0]):
                # Half hours interval
                new_hours.append(float(int(hours[0])) + 0.5)
            else:
                new_hours.append(float(hours[0]))
            
            if int(hours[1]) != float(hours[1]):
                # Half hours interval
                new_hours.append(float(int(hours[1])) + 0.5)
            else:
                new_hours.append(float(hours[1]))

            self.opening_hours[key] = new_hours

        self.cost = int(attraction_data[5])
        self.location_encoding = attraction_data[6:]

        self.categories = []
        # Each location has more than one category
        for index, encoding in enumerate(self.location_encoding):
            if int(encoding) == 1:
                self.categories.append(self.type_list[index])

        # print(self.opening_hours)


class Tourist(object):
    def __init__(self, tourist_data : list):
        self.idx = tourist_data[0]
        self.preferences = tourist_data[1].strip("[]").split(",")
        self.budget = int(tourist_data[2])
        self.must_visit = ast.literal_eval(tourist_data[3])
        self.days = int(tourist_data[4])
        self.touring_hours = ast.literal_eval(tourist_data[5])

        # Create lists and dict to hold items
        self.money_spent = 0

        # Available free time
        self.remaining_time = {}
        for i in range(self.days):
            self.remaining_time[i] = self.touring_hours

        # Format is key is day, then inside is list of Attraction Class
        # e.g. {1: ["Marina Bay", "Lau Par Sat"], 2: ["Lakeside Park"]}
        # names used for convention, but we keep track of tasks for better lookup
        self.locations = {}

        # Format is key is day, then within the visiting there is 
        # another dicitonary which contains the locations and the start time of visit
        # e.g. {1: {"Marina Bay": 8.5, "Lau Par Sat": 13}, 2: {"Lakeside Park": 7}} etc.
        self.start_times = {}


    def can_assign(self, attraction : Attraction, time : int, day : int) -> bool:
        """
        Check whether you can assign the attraction to the tourist when he visits
        at a given time at a given day
        """
        # Cannot exceed Budget
        if attraction.cost + self.money_spent > self.budget:
            return False
        
        # End time cannot be later than end of touring hours or 
        # Start time cannot be earlier as start of touring hours
        if time < self.touring_hours[0]:
            return False
        if time + attraction.task_time > self.touring_hours[1]:
            return True
        
        # 3 activities per day max
        if self.locations[day] >= 3:
            return False

        # Visitors must visit during visiting hours  
        if day not in attraction.opening_hours.keys():
            return False
        else:
            cur_opening_hours = attraction.opening_hours[day]
            # too early
            if time < cur_opening_hours[0]:
                return False
            
            # too late
            if time + attraction.task_time > cur_opening_hours[1]:
                return False

        # Make the time blocks, the add in the new task at specific time and sort 
        used_time = []
        cur_day_activities = self.locations
        cur_day_start_times = self.start_times

        for activity in cur_day_activities:
            start_time = cur_day_start_times[activity.attraction_name]
            used_time.append([start_time, start_time + activity.task_time])

        # Sort by start times
        used_time.append([time, time + attraction.task_time])
        used_time = sorted(used_time, key = lambda x : x[0])

        # At least 2 hour breaks between activities
        # Activities cannot overlap 
        for i in range(len(used_time) - 1):
            if used_time[i][1] + 2 > used_time[i+1][0]:
                return False

        return True
    
    def assign(self, attraction : Attraction, day : int, time : float) -> None:
        """
        Assign the attraction for the specific day and time
        """
        # Add attraction to the locations
        if day not in self.locations.keys():
            self.locations[day] = [attraction]
        else:
            self.locations[day].append(attraction)

        # Add the start time
        if day not in self.start_times:
            self.start_times[day] = {attraction.attraction_name : time}
        else:
            self.start_times[day][attraction.attraction_name] = time


    def remove(self, attraction : Attraction) -> None:
        """
        Remove attraction from dictionaries
        """
        for key in self.locations.keys():
            if attraction in self.locations[key]:
                self.locations[key].remove(attraction)

        # Remove the start time from the start times
        for key in self.locations.keys():
            if attraction.attraction_name in self.start_times[key].keys():
                del self.start_times[key][attraction.attraction_name]
        

### Parser to parse instance json file ###
# You should not change this class!
class Parser(object):
    def __init__(self, attraction_csv, tourist_csv):
        """
        Parse all information, turn into usable infomration
        """
        self.attraction_csv = attraction_csv
        self.tourist_csv    = tourist_csv

        self.attraction_data = []
        self.tourist_data = []

        with open(self.attraction_csv, "r") as af:
            attr_reader = csv.reader(af)

            next(attr_reader)

            for row in attr_reader:
                self.attraction_data.append(row)

        with open(self.tourist_csv, "r") as tf:
            tour_reader = csv.reader(tf)

            next(tour_reader)

            for row in tour_reader:
                self.tourist_data.append(row)
        
        # We then need to parse the data into useable data
        self.attractions = [Attraction(data, idx) for idx, data in enumerate(self.attraction_data)]
        self.tourists = [Tourist(data) for data in self.tourist_data]


class Worker(object):
    def __init__(self, data, T, bmax, wmax, rmin):
        """Initialize the worker
        Attributes:
            id::int
                id of the worker
            skills::[skill]
                a list of skills of the worker
            available::{k: v}
                key is the day, value is the list of two elements,
                the first element in the value is the first available hour for that day,
                the second element in the value is the last available hour for that day, inclusively
            bmax::int
                maximum length constraint
            wmax::int
                maximum working hours
            rmin::int
                minimum rest time
            rate::int
                hourly rate
            tasks_assigned::[task]
                a list of task objects
            blocks::{k: v}
                key is the day where a block is assigned to this worker
                value is the list of two elements
                the first element is the hour of the start of the block
                the second element is the hour of the start of the block
                if a worker is not assigned any tasks for the day, the key is removed from the blocks dictionary:
                        Eg. del self.blocks[D]

            total_hours::int
                total working hours for the worker

        """
        self.id = data["w_id"]
        self.skills = data["skills"]
        self.T = T
        self.available = {int(k): v for k, v in data["available"].items()}
        # the constant number for f2 in the objective function
        self.bmin = 4
        self.bmax = bmax
        self.wmax = wmax
        self.rmin = rmin

        self.rate = data["rate"]
        self.tasks_assigned = []
        self.blocks = {}
        self.total_hours = 0

    def can_assign(self, task):
        # // Implement Code Here
        ## check skill set

        ## check available time slots

        ## cannot do two tasks at the same time

        ## If no other tasks assigned in the same day
        #   ## check if task.hour within possible hours for current day
        #   ## check if after total_hours < wmax after adding block

        ## If there are other tasks assigned in the same day

        ## if the task fits within the existing range

        ## otherwise check if new range after task is assigned is rmin feasible

        ## check if new range after task is assigned is within bmax and wmax
        pass

    def assign_task(self, task):
        # // Implement Code Here
        pass

    def remove_task(self, task_id):
        # // Implement Code Here
        pass

    def get_objective(self):
        t = sum(x[1] - x[0] + 1 for x in self.blocks.values())
        return t * self.rate

    def __repr__(self):
        if len(self.blocks) == 0:
            return ""
        return "\n".join(
            [
                f"Worker {self.id}: Day {d} Hours {self.blocks[d]} Tasks {sorted([t.id for t in self.tasks_assigned if t.day == d])}"
                for d in sorted(self.blocks.keys())
            ]
        )


class Task(object):
    def __init__(self, data):
        self.id = data["t_id"]
        self.skill = data["skill"]
        self.day = data["day"]
        self.hour = data["hour"]


### PSP state class ###
# PSP state class. You could and should add your own helper functions to the class
# But please keep the rest untouched!
class SMJSP(State):
    def __init__(self, 
                 tourist : Tourist, 
                 attractions : List[Attraction], 
                 weighting : list = [0.5, 0.5]):
        """
        Single Machine Job Scheduling Problem

        Tourist : Tourist Class to plan for
        Attractions : List of available Attraction
        Weighting : The weighting between distances and attractiveness score
        """
        self.tourist = tourist
        self.attractions = attractions
        # the tasks assigned to each worker, eg. [worker1.tasks_assigned, worker2.tasks_assigned, ..., workerN.tasks_assigned]
        self.solution = []
        self.unassigned = list(attractions)

    def random_initialize(self, seed=None):
        """
        Args:
            seed::int
                random seed
        Returns:
            objective::float
                objective value of the state
        """
        if seed is None:
            seed = 606

        random.seed(seed)
        # -----------------------------------------------------------
        # // Implement Code Here
        # // This should contain your construction heuristic for initial solution
        # // Use Worker class methods to check if assignment is valid
        # -----------------------------------------------------------

        # We assign each must visit to the tourist first, before assigning the tasks
        # Assign each task as early as possible, we randomly draw some tasks first
        attr_to_choose = self.attractions


    def copy(self):
        return copy.deepcopy(self)

    def objective(self):
        """Calculate the objective value of the state
        Return the total cost of each worker + unassigned cost
        """
        f1 = len(self.unassigned)
        f2 = sum(max(worker.get_objective(), 50) for worker in self.workers if worker.get_objective() > 0)
        return self.Alpha * f1 + f2
