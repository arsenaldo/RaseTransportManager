from DBhelper import DBhelper
from MapExecuter import MapExecuter
import datetime
import copy
import operator
from RaseReader import RaseReader

DURATION = 1
FROM = 2
TO = 3
ROUTE = 4

matrix = []
races = []
fly_time = {}


def hello():
    pass


def fill_matrix(places):
    global matrix
    matrix = [[0 for i in range(len(places))] for j in range(len(places))]
    print(places)


def find_trace_by_place_id_first(traces, p_from_id):
    found_traces = []
    for i in range(len(traces)):
        if traces[i][FROM] == p_from_id:
            found_traces.append(traces[i])
    return found_traces


def find_trace_by_place_id(traces, p_from_id, route_id):
    global fly_time
    found_traces = []
    for i in range(len(traces)):
        if traces[i][FROM] == p_from_id and traces[i][ROUTE] == route_id:
            found_traces.append(traces[i])
            try:
                fly_time[route_id] += traces[i][DURATION]
            except:
                fly_time[route_id] = 0
                fly_time[route_id] += traces[i][DURATION]
    if len(found_traces) == 0:
        return
    for f_tr in found_traces:
        matrix[p_from_id - 1][f_tr[TO] - 1] = 1
        find_trace_by_place_id(traces, f_tr[TO], route_id)


def routes(places, traces, p_from, p_to):
    p_from_id = None
    for i in range(len(places)):
        if places[i][1] == p_from:
            p_from_id = places[i][0]
    found_traces_first = find_trace_by_place_id_first(traces, p_from_id)
    for trace in found_traces_first:
        find_trace_by_place_id(traces, trace[FROM], trace[ROUTE])


def normalize_map_list(map_list):
    map_to_del = []
    n = 0
    m = 0
    while n < len(map_list):
        id_from = map_list[n].place_from_id
        id_to = map_list[n].place_to_id
        route = map_list[n].route
        while m < len(map_list):
            if n == m:
                m += 1
            elif map_list[m].place_from_id == id_from and \
                    map_list[m].place_to_id == id_to and \
                    map_list[m].route == route:
                map_to_del.append(copy.deepcopy(map_list[m]))
                m += 1
            else:
                m += 1
        n += 1
        m = 0
    repeat_by_routes = {}
    for ml in map_to_del:
        try:
            repeat_by_routes[str(ml.place_from_id) + \
                             str(ml.place_to_id) + \
                             str(ml.route)] \
                .append(copy.deepcopy(ml))
        except:
            repeat_by_routes[str(ml.place_from_id) + \
                             str(ml.place_to_id) + \
                             str(ml.route)] = []
            repeat_by_routes[str(ml.place_from_id) + \
                             str(ml.place_to_id) + \
                             str(ml.route)] \
                .append(copy.deepcopy(ml))
    for ml in repeat_by_routes:
        to_del = max(repeat_by_routes[ml], key=lambda x: x.region_density)
        for map_item in map_list:
            if str(map_item) == str(to_del):
                map_list.remove(map_item)


def get_trace_shorts_by_route(routes, db_helper):
    traces = []
    for route in routes:
        result = db_helper.get_trace_shorts_by_route(str(route[0]))
        for res in result:
            traces.append(copy.deepcopy(res))
    print("TRACES BY ROUTES")
    for tr in traces:
        print(tr)


def get_trace_short_by_rases_for_other(rases_in_time_diapozon, db_helper):
    traces = []
    for rase in rases_in_time_diapozon:
        result = db_helper.get_trace_shorts_by_route(str(rase[6]))
        for res in result:
            traces.append(copy.deepcopy(res))
    print("TRACES BY RASES")
    for tr in traces:
        print(tr)


def fill_up_trace_short_density(our_map_list, other_map_list):
    for omp in our_map_list:
        for other_mp in other_map_list:
            if (other_mp.place_from_id == omp.place_from_id and other_mp.place_to_id == omp.place_to_id) or \
                    (other_mp.place_to_id == omp.place_from_id and other_mp.place_from_id == omp.place_to_id):
                print("SIMILAR ", other_mp, omp)
                omp.trace_reg_dict['cur_density'] += 1
            # input()
            else:
                print("NOPE SIMILARS", omp, other_mp)
            # input()
    print("TOTALLY")
    for omp in our_map_list:
        print(omp)


# input()

def check_route_density(our_map_list):
    for omp in our_map_list:
        if omp.trace_reg_dict['cur_density'] > omp.region_density:
            return False
    return True


def check_rase_time(time_away, rases_from_diapozon, route):
    print("CHECK TIME_AWAY")
    print(time_away)
    for rase in rases_from_diapozon:
        print(rase[1], route, rase[6])
        # print(datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))
        if abs((rase[1] - datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))) \
                .total_seconds() < 1800 and route == rase[6]:
            return False

    input()
    return True


def check_rase_time_with_group(time_away, other_rase, city, route, other_map_list):
    print("CHECK TIME_AWAY")
    print(time_away)
    print(other_rase[1], route, other_rase[6])
    # print(datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))
    db_helper = DBhelper()
    routes_deny = db_helper.find_routes_group_by_from(city, int(route))
    print("RASE TEST ", other_rase, route, other_map_list[0])
    print("routes deny ", routes_deny, city, str(route))
    input()

    if abs((other_rase[1] - datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))) \
            .total_seconds() < 1800 and route == other_rase[6]:
        print("CANT1")
        return False

    if other_map_list[0].place_from_name == city:
        for route_list in routes_deny[city]:
            if other_map_list[0].route in routes_deny[city][route_list] and route in routes_deny[city][route_list]:
                if abs((other_rase[1] - datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))) \
                        .total_seconds() < 1800:
                    print("CANT2")
                    return False

    input()
    return True

def merge_rases_by_time_later(routes, rase_reader, db_helper):
    all_rases = db_helper.get("rase")
    merged = []
    merge_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
    for rase in all_rases:
        if rase[6] in routes and rase[1] >= merge_time:
            merged.append(copy.deepcopy(rase))
    return merged

def merge_rases_by_time_earlier(routes, rase_reader, db_helper):
    all_rases = db_helper.get("rase")
    merged = []
    merge_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
    for rase in all_rases:
        if rase[6] in routes and rase[1] >= merge_time:
            merged.append(copy.deepcopy(rase))
    return merged

def move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper, m_fly_time):
    our_time = down_rase[1] + datetime.timedelta(minutes=30)
    time_fly = datetime.timedelta(minutes=int(m_fly_time[down_rase[6]]) + 1)
    time_come = our_time + time_fly
    our_rase = (our_time, time_come, time_fly, rase_reader.company, rase_reader.plane, down_rase[6])
    print("MOVE FROM EARLIER ", our_rase)
    input()
    move_rases_below_if_necessary(our_rase, rases_later_by_route, rase_reader, db_helper)
    return our_rase

def move_rases_below_if_necessary(our_rase, route_rases_later, rase_reader, db_helper):
    print("MOVE IF NECESSARY")
    route_rases_later = list(route_rases_later)
    route = route_rases_later[0][6]
    routes_group = db_helper.find_routes_group_by_from(rase_reader.city_from, route)
    print("ROUTES GROUP")
    print(routes_group)
    for el in routes_group[rase_reader.city_from]:
        if route in routes_group[rase_reader.city_from][el]:
            route_rases_later = merge_rases_by_time_later(routes_group[rase_reader.city_from][el], rase_reader, db_helper)
            route_rases_later.sort(key=lambda x: x[1])

            print("MERGED RASES")
            for rase in route_rases_later:
                print(rase)

    time_to_move = our_rase[0] - route_rases_later[0][1] + datetime.timedelta(minutes=30)
    print("TIME TO MOVE")
    print(our_rase[0])
    print(route_rases_later[0][1])
    print(time_to_move)
    rase_to_move = (route_rases_later[0][0],
                    route_rases_later[0][1] + time_to_move,
                    route_rases_later[0][2] + time_to_move,
                    route_rases_later[0][3],
                    route_rases_later[0][4],
                    route_rases_later[0][5],
                    route_rases_later[0][6])
    print("RASE TO UPDATE ", rase_to_move)
    input()
    db_helper.update_rase(rase_to_move)
    route_rases_later[0] = copy.deepcopy(rase_to_move)
    step = 0
    while step < len(route_rases_later) - 1:
        print("TEST MOVE NEXT")
        print(route_rases_later[step + 1][1])
        print(route_rases_later[step][1])
        if route_rases_later[step + 1][1] - route_rases_later[step][1] < datetime.timedelta(minutes=30):
            time_to_move = route_rases_later[step][1] - route_rases_later[step + 1][1] + datetime.timedelta(minutes=30)
            print("TIME TO MOVE")
            print(route_rases_later[step][1])
            print(route_rases_later[step + 1][1])
            print(time_to_move)
            rase_to_move = (route_rases_later[step + 1][0],
                            route_rases_later[step + 1][1] + time_to_move,
                            route_rases_later[step + 1][2] + time_to_move,
                            route_rases_later[step + 1][3],
                            route_rases_later[step + 1][4],
                            route_rases_later[step + 1][5],
                            route_rases_later[step + 1][6])
            route_rases_later[step + 1] = copy.deepcopy(rase_to_move)
            print("RASE TO UPDATE ", rase_to_move)
            input()
            db_helper.update_rase(rase_to_move)
        step += 1


def fiasco_handle(rase_reader, db_helper, m_fly_time):

    rases_later = db_helper.get_rase_later(rase_reader.city_from, rase_reader.time_away)
    rases_earlier = db_helper.get_rase_earlier(rase_reader.city_from, rase_reader.time_away)
    our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")

    num_try = 0
    optim_routes = set()
    not_optim_routes = set()
    diff_time = []

    if len(rases_later) == 0:
        for rase in rases_earlier:
            diff_time.append(our_time - rase[1])
        print(diff_time[diff_time.index(max(diff_time))])
        print("OPTIM")
        print(rases_earlier[diff_time.index(max(diff_time))][6])
        optim_route = rases_earlier[diff_time.index(max(diff_time))][6]
        time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
        time_come = our_time + time_fly
        our_company = rase_reader.company
        our_plane = rase_reader.plane
        our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
        print("OUR RASE")
        print(our_rase)
        db_helper.insert_rase_tuple(our_rase)
        return

    if len(rases_earlier) == 0:
        for rase in rases_earlier:
            diff_time.append(rase[1] - our_time)
        print(diff_time[diff_time.index(max(diff_time))])
        print("OPTIM")
        print(rases_earlier[diff_time.index(max(diff_time))][6])
        optim_route = rases_earlier[diff_time.index(max(diff_time))][6]
        time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
        time_come = our_time + time_fly
        our_company = rase_reader.company
        our_plane = rase_reader.plane
        our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
        print("OUR RASE")
        print(our_rase)
        rases_later_by_route = db_helper.get_rase_later_by_route(optim_route, rase_reader.time_away)
        move_rases_below_if_necessary(our_rase, rases_later_by_route, rase_reader, db_helper)
        db_helper.insert_rase_tuple(our_rase)
        return

    while True:
        print("rases later")
        print(rases_later)
        print("Len")
        print(len(rases_later))
        print(num_try)
        up_rase = rases_later[num_try]
        down_rase = rases_earlier[0]

        print("UP RASE, DOWN RASE")
        print(up_rase)
        print(down_rase)

        print("need to move next rases")
        our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
        print(up_rase[6])
        pre_rases = db_helper.get_rase_earlier_by_route(up_rase[6],
                                                               rase_reader.time_away)
        print("PRE RASES")
        print(pre_rases)
        if len(pre_rases) > 0:
            rase_earlier = pre_rases[0]
            rases_later_by_route = db_helper.get_rase_later_by_route(up_rase[6], rase_reader.time_away)
            print("OUR TIME, RASE EARLIER")
            print(our_time)
            print(rase_earlier)
            if our_time - rase_earlier[1] >= datetime.timedelta(minutes=30):
                print("move next")
                optim_routes.add(copy.deepcopy(rase_earlier[6]))
                if num_try >= len(rases_later) - 1:
                    if len(optim_routes) > 0:
                        print("SELECT MOST OPTIM ROUTE")
                        break
                    print("move us and next")
                    our_rase = move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper, m_fly_time)
                    db_helper.insert_rase_tuple(our_rase)
                    break
                num_try += 1
            else:
                if num_try >= len(rases_later) - 1:
                    if len(optim_routes) > 0:
                        print("SELECT MOST OPTIM ROUTE")
                        break
                    print("move us and next")

                    print("NOT OPTIM ROUTES")
                    not_opt_rout_helper = list(not_optim_routes)
                    m_fly_time = sorted(m_fly_time.items(), key= lambda x: x[1])
                    m_fly_time = dict((key, value) for key, value in m_fly_time)
                    not_optim_routes = [r for r in m_fly_time if r in not_opt_rout_helper]
                    print(not_optim_routes)
                    our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
                    for op_route in not_optim_routes:
                        opt_rase = db_helper.get_rase_earlier_by_route(up_rase[6],
                                                                       rase_reader.time_away)[0]
                        diff_time.append(our_time - opt_rase[1])
                    print("DIFF TIME")
                    print(diff_time)
                    print("MAX")
                    print(diff_time[diff_time.index(max(diff_time))])
                    print("NOT OPTIM")
                    print(not_optim_routes[diff_time.index(max(diff_time))])
                    optim_route = not_optim_routes[diff_time.index(max(diff_time))]
                    time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
                    time_come = our_time + time_fly
                    our_company = rase_reader.company
                    our_plane = rase_reader.plane
                    our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
                    print("OUR RASE")
                    print(our_rase)
                    rases_later_by_route = db_helper.get_rase_later_by_route(optim_route, rase_reader.time_away)
                    print("RASES LATER BY ROUTE")
                    for r in rases_later_by_route:
                        print(r)
                    down_rase = db_helper.get_rase_earlier_by_route(optim_route,
                                                                       rase_reader.time_away)[0]
                    our_rase = move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper,
                                                      m_fly_time)
                    db_helper.insert_rase_tuple(our_rase)
                    #move_rases_below_if_necessary(our_rase, rases_later_by_route, rase_reader, db_helper)
                    #db_helper.insert_rase_tuple(our_rase)
                    return

                    our_rase = move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper, m_fly_time)
                    db_helper.insert_rase_tuple(our_rase)
                    return
                else:
                    print("TRY ANOTHER UP RASE, NOT ", up_rase[6])
                    print("NUM TRY ", num_try)
                    not_optim_routes.add(up_rase[6])
                    input()
                    num_try += 1
        else:
            if num_try >= len(rases_later) - 1:
                print("CHECK 2")
                break
            else:
                print("move next")
                optim_routes.add(copy.deepcopy(up_rase[6]))
                num_try += 1

    print("OPTIM ROUTES")
    opt_rout_helper = list(optim_routes)
    m_fly_time = sorted(m_fly_time.items(), key=lambda x: x[1])
    m_fly_time = dict((key, value) for key, value in m_fly_time)
    optim_routes = [r for r in m_fly_time if r in opt_rout_helper]
    print(optim_routes)
    our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
    for op_route in optim_routes:
        opt_rase = db_helper.get_rase_later_by_route(op_route, rase_reader.time_away)[0]
        diff_time.append(opt_rase[1] - our_time)
    print("DIFF TIME")
    print(diff_time)
    print("MAX")
    print(diff_time[diff_time.index(max(diff_time))])
    print("OPTIM")
    print(optim_routes[diff_time.index(max(diff_time))])
    optim_route = optim_routes[diff_time.index(max(diff_time))]
    time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
    time_come = our_time + time_fly
    our_company = rase_reader.company
    our_plane = rase_reader.plane
    our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
    print("OUR RASE")
    print(our_rase)
    rases_later_by_route = db_helper.get_rase_later_by_route(optim_route, rase_reader.time_away)
    print("RASES LATER BY ROUTE")
    for r in rases_later_by_route:
        print(r)
    move_rases_below_if_necessary(our_rase, rases_later_by_route, rase_reader, db_helper)
    db_helper.insert_rase_tuple(our_rase)
    return

def main(*args):
    global fly_time
    fly_time = {}
    delay_state = False
    breaker = False
    db_helper = DBhelper()
    trace_list = db_helper.get("trace_short")
    place_list = db_helper.get("place")
    fill_matrix(place_list)
    routes(place_list, trace_list, "St.Petersberg, Pulkovo", "")
    routes(place_list, trace_list, "Sheremetievo.Sunab", "")
    print("matrix")
    i = 0
    for row in matrix:
        i += 1
        print(row, i)
    m_fly_time = copy.deepcopy(fly_time)
    for key in m_fly_time:
        m_fly_time[key] *= 60

    print("FLY TIME")
    print(m_fly_time)
    input()

    rase_reader = RaseReader(*args)
    rase_routes = rase_reader.get_routes_by_rase(db_helper)

    while True:
        if not delay_state:
            print("ROUTES FROM ", rase_routes[0][1], " TO ", rase_routes[0][2])
            for route in rase_routes:
                print(route)
        else:
            fiasco_handle(rase_reader, db_helper, m_fly_time)
            return
        time_worker = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
        input()
        time_delta = datetime.timedelta(hours=1, minutes=30)
        top_time_border = time_worker + time_delta
        bottom_time_border = time_worker - time_delta
        print(time_worker)
        print(time_delta)
        print(top_time_border)
        print(bottom_time_border)
        input()
        rases_in_time_diapozon = db_helper.get_rase_from_diapozon(str(top_time_border), str(bottom_time_border))
        print("RASES FROM DIAPOZON ", top_time_border, bottom_time_border)
        for rase in rases_in_time_diapozon:
            print(rase)

        map_exec = MapExecuter()
        print(map_exec)
        for our_rase in rase_routes:
            our_map_list = map_exec.execute_by_route(route=str(our_rase[0]))
            normalize_map_list(our_map_list)
            print("TSHOW OUR MAP LIST")
            print("ROUTE ", str(our_rase[0]))
            for omp in our_map_list:
                omp.trace_reg_dict['cur_density'] = 0
                print(omp)
            input()
            for other_rase in rases_in_time_diapozon:
                other_map_list = map_exec.execute_by_route(route=str(other_rase[6]))
                normalize_map_list(other_map_list)
                print("OTHER RASE ", str(other_rase[6]))
                for other_mp in other_map_list:
                    print(other_mp)
                input()
                print("CHECK TIME")
                #if not check_rase_time(rase_reader.time_away, rases_in_time_diapozon, omp.route):
                if not check_rase_time_with_group(rase_reader.time_away, \
                                                  other_rase, \
                                                  args[1], \
                                                  omp.route, \
                                                  other_map_list):
                    print("CAN NOT INSERT IN THIS TIME. IT'S BUSY")
                    delay_state = True
                    breaker = True
                    print("GO TO ANATHOR ROUTE")
                    input()
                    break
                else:
                    breaker = False
                    fill_up_trace_short_density(our_map_list, other_map_list)
            if breaker:
                continue

            if check_route_density(our_map_list):
                delay_state = False
                print("OK WE CAN PUT THIS RASE IN THIS TIME")
                print("TIME_AWAY: ", rase_reader.time_away)
                t_away = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
                t_fly = datetime.timedelta(minutes=int(m_fly_time[our_rase[0]]) + 1)
                t_come = t_away + t_fly
                print("TIME COME: ", t_come)
                print("TIME FLY: ", t_fly)
                print("ROUTE: ", our_rase[0])
                input()
                rase = (
                    str(t_away),
                    str(t_come),
                    str(t_fly),
                    rase_reader.company,
                    rase_reader.plane,
                    str(our_rase[0])
                )
                print(rase)
                print("GONNA INSERT")
                input()
                db_helper.insert_rase_tuple(rase)
                input()
                return
            else:
                print("IMPOSSIBLE TO PUT THIS RASE IN THIS TIME")
                print("DELAY 30 MIN")
                delay_state = True
                input()
        print("#########################")
        print("#########FIASCO##########")
        print("#########################")
        input()
