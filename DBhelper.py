import pymysql.cursors
import copy
import datetime

class DBhelper:
    def __init__(self,
                 host='localhost',
                 user='root',
                 password='root',
                 db='diplom_rase'):

        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password='root',
                                          db='diplom_rase')

    def get(self, table_name):
        my_list = []
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM " + table_name
                cursor.execute(sql)
                result = cursor.fetchall()
                for res in result:
                    my_list.append(res)
        except:
            print("GET " + table_name + " error")
        return my_list

    def get_city_id_by_name(self, city_name):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT id FROM `place` WHERE name = %s"
                cursor.execute(sql, (city_name))
                result = cursor.fetchone()
                return result[0]
        except:
            print("GET CITY ERROR")
        return None

    def get_routes_by_from_to(self, city_from, city_to):
        routes = []
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM `route` WHERE city_from = %s AND city_to = %s"
                cursor.execute(sql, (city_from, city_to))
                result = cursor.fetchall()
                for res in result:
                    routes.append(copy.deepcopy(res))
        except:
            print("GET ROUTE ERROR")
        return routes

    def get_rase_from_diapozon(self, low, top):
        rases = []
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM `rase` WHERE time_away < %s AND time_come > %s"
                cursor.execute(sql, (low, top))
                result = cursor.fetchall()
                for res in result:
                    rases.append(copy.deepcopy(res))
        except:
            print("GET RASES ERROR")
        return rases

    def get_trace_shorts_by_route(self, route):
        trace_shorts = []
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM `trace_short` WHERE route = %s"
                cursor.execute(sql, (route))
                result = cursor.fetchall()
                for res in result:
                    trace_shorts.append(copy.deepcopy(res))
        except:
            print("GET TRACE_SHORT ERROR")
        return trace_shorts

    def insert_rase(self, rase):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `rase` VALUES (NULL, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, rase.get_items())
        self.connection.commit()

    def insert_rase_tuple(self, rase):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `rase` VALUES (NULL, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, rase)
        self.connection.commit()

    def select_rase_to_move(self, time_away, city_from):
        with self.connection.cursor() as cursor:
            t = datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S")
            new_time = t + datetime.timedelta(minutes=30)
            sql = "SELECT * FROM rase WHERE time_away >= %s" + \
                  " AND time_away <= %s AND route in" + \
                  " (select route from rase JOIN route ON rase.route = route.id where city_from = %s)" + \
                  " order by time_away DESC limit 1"
            cursor.execute(sql, (str(t), str(new_time), str(city_from)))
            result = cursor.fetchall()
            return result[0]

    def select_rase_above_before_moving(self, time_away, city_from):
        with self.connection.cursor() as cursor:
            t = datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S")
            sql = "SELECT * FROM rase WHERE time_away < %s" + \
                  " AND route in" + \
                  " (select route from rase JOIN route ON rase.route = route.id where city_from = %s)" + \
                  " order by time_away DESC limit 1"
            cursor.execute(sql, (str(t), str(city_from)))
            result = cursor.fetchall()
            return result[0]

    def select_rases_below(self, rase):
        with self.connection.cursor() as cursor:
            time_away = rase[1]
            route = rase[6]
            sql = "Select * FROM rase where time_away >= %s AND rase.route = %s ORDER BY time_away"
            cursor.execute(sql, (time_away, route))
            result = cursor.fetchall()
            return result

    def update_rase(self, old_rase):
        with self.connection.cursor() as cursor:
            sql = "UPDATE rase SET rase.time_away = %s, rase.time_come = %s WHERE rase.id = %s"
            cursor.execute(sql, (str(old_rase[1]), str(old_rase[2]), str(old_rase[0])))
            result = cursor.fetchall()

    def find_routes_group_by_from(self, city, route):
        with self.connection.cursor() as cursor:
            sql = "select p_f.name, p_t.name, trace_short.route " \
                + "from route as r join trace_short on trace_short.route = r.id " \
                + "join place as p_f on trace_short.place_from = p_f.id " \
                + "join place as p_t on trace_short.place_to = p_t.id " \
                + "where p_f.name like " \
                + "(select distinct s_r.city_from from route as s_r join place where s_r.id = %s) "\
                + "order by p_t.name"

            cursor.execute(sql, (route))
            result = cursor.fetchall()
            my_list = []
            for res in result:
                my_list.append(copy.deepcopy(res[1]))
            i = 0
            while i < len(my_list):
                if my_list.count(my_list[i]) == 1:
                    del my_list[i]
                    continue
                else:
                    i += 1
            my_set = set(my_list)
            route_dict = {}
            route_dict_dest = {}
            route_dict[city] = route_dict_dest
            for res in result:
                if res[1] in my_set:
                    try:
                        route_dict_dest[res[1]].append(copy.deepcopy(res[2]))
                    except KeyError:
                        route_dict_dest[res[1]] = []
                        route_dict_dest[res[1]].append(copy.deepcopy(res[2]))
            return route_dict


    def get_rase_later(self, city, time_away):
        with self.connection.cursor() as cursor:
            sql = "select * from rase " \
                  + "join route on rase.route = route.id " \
                  + "where route.city_from = %s " \
                  + "and rase.time_away >= %s " \
                  + "order by time_away, time_fly"
            cursor.execute(sql, (city, time_away))
            result = cursor.fetchall()
            return result

    def get_rase_earlier(self, city, time_away):
        with self.connection.cursor() as cursor:
            sql = "select * from rase " \
                + "join route on rase.route = route.id " \
                + "where route.city_from = %s "\
                + "and rase.time_away < %s "\
                + "order by time_away DESC, time_fly"
            cursor.execute(sql, (city, time_away))
            result = cursor.fetchall()
            return result

    def get_rase_earlier_by_route(self, route, time_away):
        with self.connection.cursor() as cursor:
            sql = "select * from rase where rase.route = %s and time_away < %s " \
                + "order by rase.time_away DESC, rase.time_fly"
            cursor.execute(sql, (route, time_away))
            result = cursor.fetchall()
            return result

    def get_rase_later_by_route(self, route, time_away):
        with self.connection.cursor() as cursor:
            sql = "select * from rase where rase.route = %s and time_away >= %s " \
                  + "order by rase.time_away, rase.time_fly"
            cursor.execute(sql, (route, time_away))
            result = cursor.fetchall()
            return result