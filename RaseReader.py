
import datetime
from DBhelper import DBhelper


# Pulkovo
# Sheremetievo.Sunab

class RaseReader:

    def __init__(self, *args):
        self.time_away = args[0]
        self.city_from = args[1]
        self.city_to = args[2]
        self.company = args[3]
        self.plane = args[4]

    def get_routes_by_rase(self, db_helper):
        # self.time_away = str(input("time away:_ (2018-05-05 12:30:00) "))
        # self.plane = str(input("plane:_ (Boing747) "))
        # self.company = str(input("company:_ (AeroFlot) "))
        # self.city_from = str(input("city from:_ (St.Petersberg, Pulkovo | Moscow, Sheremetyevo) "))
        # self.city_to = str(input("city to:_ (St.Petersberg, Pulkovo | Moscow, Sheremetyevo) "))
        # datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')

        # self.time_away = "2018-05-05 12:30:00"
        # self.plane = "Boing747"
        # self.company = "AeroFlot"
        # self.city_from = "St.Petersberg, Pulkovo"

        # self.city_to = "Moscow, Sheremetyevo"

        print(self.time_away)
        print(self.plane)
        print(self.company)
        print(self.city_from)
        print(self.city_to)
        input()
        routes = db_helper.get_routes_by_from_to(self.city_from, self.city_to)
        print(routes)
        input()
        return routes
