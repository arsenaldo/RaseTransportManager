
import datetime
from DBhelper import DBhelper

class RaseReader:

    def __init__(self, *args):
        self.time_away = args[0]
        self.city_from = args[1]
        self.city_to = args[2]
        self.company = args[3]
        self.plane = args[4]

    def get_routes_by_rase(self, db_helper):
        routes = db_helper.get_routes_by_from_to(self.city_from, self.city_to)
        return routes
