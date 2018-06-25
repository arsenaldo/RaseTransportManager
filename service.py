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

def fill_matrix(places):
    global matrix
    matrix = [[0 for i in range(len(places))] for j in range(len(places))]

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

def get_trace_short_by_rases_for_other(rases_in_time_diapozon, db_helper):
    traces = []
    for rase in rases_in_time_diapozon:
        result = db_helper.get_trace_shorts_by_route(str(rase[6]))
        for res in result:
            traces.append(copy.deepcopy(res))

def fill_up_trace_short_density(our_map_list, other_map_list):
    for omp in our_map_list:
        for other_mp in other_map_list:
            if (other_mp.place_from_id == omp.place_from_id and other_mp.place_to_id == omp.place_to_id) or \
                    (other_mp.place_to_id == omp.place_from_id and other_mp.place_from_id == omp.place_to_id):
                omp.trace_reg_dict['cur_density'] += 1
            else:
                pass

def check_route_density(our_map_list):
    for omp in our_map_list:
        if omp.trace_reg_dict['cur_density'] > omp.region_density:
            return False
    return True

def check_rase_time(time_away, rases_from_diapozon, route):
    for rase in rases_from_diapozon:
        if abs((rase[1] - datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))) \
                .total_seconds() < 1800 and route == rase[6]:
            return False
    return True

def check_rase_time_with_group(time_away, other_rase, city, route, other_map_list):
    db_helper = DBhelper()
    routes_deny = db_helper.find_routes_group_by_from(city, int(route))
    if abs((other_rase[1] - datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))) \
            .total_seconds() < 1800 and route == other_rase[6]:
        return False

    if other_map_list[0].place_from_name == city:
        for route_list in routes_deny[city]:
            if other_map_list[0].route in routes_deny[city][route_list] and route in routes_deny[city][route_list]:
                if abs((other_rase[1] - datetime.datetime.strptime(time_away, "%Y-%m-%d %H:%M:%S"))) \
                        .total_seconds() < 1800:
                    return False
    return True

def merge_rases_by_time_later(routes, rase_reader, db_helper):
    all_rases = db_helper.get("rase")
    merged = []
    merge_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
    for rase in all_rases:
        if rase[6] in routes and rase[1] >= merge_time:
            merged.append(copy.deepcopy(rase))
    merged.sort(key=lambda x: x[1])
    return merged

def merge_rases_by_time_earlier(routes, rase_reader, db_helper):
    all_rases = db_helper.get("rase")
    merged = []
    merge_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
    for rase in all_rases:
        if rase[6] in routes and rase[1] < merge_time:
            merged.append(copy.deepcopy(rase))
    merged.sort(key = lambda x: x[1], reverse=True)
    return merged

def move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper, m_fly_time):
    our_time = down_rase[1] + datetime.timedelta(minutes=30)
    time_fly = datetime.timedelta(minutes=int(m_fly_time[down_rase[6]]) + 1)
    time_come = our_time + time_fly
    our_rase = (our_time, time_come, time_fly, rase_reader.company, rase_reader.plane, down_rase[6])
    move_rases_below_if_necessary(our_rase, rases_later_by_route, rase_reader, db_helper)
    return our_rase

def move_rases_below_if_necessary(our_rase, route_rases_later, rase_reader, db_helper):
    route_rases_later = list(route_rases_later)
    route = route_rases_later[0][6]
    routes_group = db_helper.find_routes_group_by_from(rase_reader.city_from, route)
    for el in routes_group[rase_reader.city_from]:
        if route in routes_group[rase_reader.city_from][el]:
            route_rases_later = merge_rases_by_time_later(routes_group[rase_reader.city_from][el], rase_reader, db_helper)
            route_rases_later.sort(key=lambda x: x[1])
    time_to_move = our_rase[0] - route_rases_later[0][1] + datetime.timedelta(minutes=30)
    rase_to_move = (route_rases_later[0][0],
                    route_rases_later[0][1] + time_to_move,
                    route_rases_later[0][2] + time_to_move,
                    route_rases_later[0][3],
                    route_rases_later[0][4],
                    route_rases_later[0][5],
                    route_rases_later[0][6])
    db_helper.update_rase(rase_to_move)
    route_rases_later[0] = copy.deepcopy(rase_to_move)
    step = 0
    while step < len(route_rases_later) - 1:
        if route_rases_later[step + 1][1] - route_rases_later[step][1] < datetime.timedelta(minutes=30):
            time_to_move = route_rases_later[step][1] - route_rases_later[step + 1][1] + datetime.timedelta(minutes=30)
            rase_to_move = (route_rases_later[step + 1][0],
                            route_rases_later[step + 1][1] + time_to_move,
                            route_rases_later[step + 1][2] + time_to_move,
                            route_rases_later[step + 1][3],
                            route_rases_later[step + 1][4],
                            route_rases_later[step + 1][5],
                            route_rases_later[step + 1][6])
            route_rases_later[step + 1] = copy.deepcopy(rase_to_move)
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
    w_rases_earlier = []
    w_rases_later = []

    if len(rases_later) == 0:
        for rase in rases_earlier:
            diff_time.append(our_time - rase[1])
        optim_route = rases_earlier[diff_time.index(max(diff_time))][6]
        time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
        time_come = our_time + time_fly
        our_company = rase_reader.company
        our_plane = rase_reader.plane
        our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
        db_helper.insert_rase_tuple(our_rase)
        return

    if len(rases_earlier) == 0:
        for rase in rases_earlier:
            diff_time.append(rase[1] - our_time)
        optim_route = rases_earlier[diff_time.index(max(diff_time))][6]
        time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
        time_come = our_time + time_fly
        our_company = rase_reader.company
        our_plane = rase_reader.plane
        our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
        rases_later_by_route = db_helper.get_rase_later_by_route(optim_route, rase_reader.time_away)
        move_rases_below_if_necessary(our_rase, rases_later_by_route, rase_reader, db_helper)
        db_helper.insert_rase_tuple(our_rase)
        return

    while True:
        up_rase = rases_later[num_try]
        down_rase = rases_earlier[0]
        our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
        routes_deny = db_helper.find_routes_group_by_from(rase_reader.city_from, up_rase[6])
        for key in routes_deny[rase_reader.city_from]:
            if up_rase[6] in routes_deny[rase_reader.city_from][key]:
                w_rases_earlier = merge_rases_by_time_earlier(
                                        routes_deny[rase_reader.city_from][key],
                                        rase_reader,
                                        db_helper
                                        )
                w_rases_later = merge_rases_by_time_later(
                                        routes_deny[rase_reader.city_from][key],
                                        rase_reader,
                                        db_helper
                                        )
        if len(w_rases_earlier) == 0:
            w_rases_earlier = db_helper.get_rase_earlier_by_route(up_rase[6],
                                                               rase_reader.time_away)
        if len(w_rases_earlier) > 0:
            rase_earlier = w_rases_earlier[0]
            rases_later_by_route = []
            if len(w_rases_later) == 0:
                rases_later_by_route = db_helper.get_rase_later_by_route(up_rase[6], rase_reader.time_away)
            else:
                rases_later_by_route = w_rases_later
            if our_time - rase_earlier[1] >= datetime.timedelta(minutes=30):
                optim_routes.add(copy.deepcopy(rase_earlier[6]))
                if num_try >= len(rases_later) - 1:
                    if len(optim_routes) > 0:
                        break
                    our_rase = move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper, m_fly_time)
                    db_helper.insert_rase_tuple(our_rase)
                    break
                num_try += 1
            else:
                if num_try >= len(rases_later) - 1:
                    if len(optim_routes) > 0:
                        break
                    not_opt_rout_helper = list(not_optim_routes)
                    m_fly_time = sorted(m_fly_time.items(), key= lambda x: x[1])
                    m_fly_time = dict((key, value) for key, value in m_fly_time)
                    not_optim_routes = [r for r in m_fly_time if r in not_opt_rout_helper]
                    our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
                    for op_route in not_optim_routes:
                        opt_rase = db_helper.get_rase_earlier_by_route(up_rase[6],
                                                                       rase_reader.time_away)[0]
                        diff_time.append(our_time - opt_rase[1])
                    optim_route = not_optim_routes[diff_time.index(max(diff_time))]
                    time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
                    time_come = our_time + time_fly
                    our_company = rase_reader.company
                    our_plane = rase_reader.plane
                    our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
                    rases_later_by_route = db_helper.get_rase_later_by_route(optim_route, rase_reader.time_away)
                    down_rase = db_helper.get_rase_earlier_by_route(optim_route,
                                                                       rase_reader.time_away)[0]
                    our_rase = move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper,
                                                      m_fly_time)
                    db_helper.insert_rase_tuple(our_rase)
                    return

                    our_rase = move_rase_from_earlier(rase_reader, down_rase, rases_later_by_route, db_helper, m_fly_time)
                    db_helper.insert_rase_tuple(our_rase)
                    return
                else:
                    not_optim_routes.add(up_rase[6])
                    num_try += 1
        else:
            if num_try >= len(rases_later) - 1:
                break
            else:
                optim_routes.add(copy.deepcopy(up_rase[6]))
                num_try += 1

    opt_rout_helper = list(optim_routes)
    m_fly_time = sorted(m_fly_time.items(), key=lambda x: x[1])
    m_fly_time = dict((key, value) for key, value in m_fly_time)
    optim_routes = [r for r in m_fly_time if r in opt_rout_helper]
    our_time = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
    for op_route in optim_routes:
        opt_rase = db_helper.get_rase_later_by_route(op_route, rase_reader.time_away)[0]
        diff_time.append(opt_rase[1] - our_time)
    optim_route = optim_routes[diff_time.index(max(diff_time))]
    time_fly = datetime.timedelta(minutes=int(m_fly_time[optim_route]) + 1)
    time_come = our_time + time_fly
    our_company = rase_reader.company
    our_plane = rase_reader.plane
    our_rase = (our_time, time_come, time_fly, our_company, our_plane, optim_route)
    rases_later_by_route = db_helper.get_rase_later_by_route(optim_route, rase_reader.time_away)
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
    i = 0
    for row in matrix:
        i += 1
    m_fly_time = copy.deepcopy(fly_time)
    for key in m_fly_time:
        m_fly_time[key] *= 60

    rase_reader = RaseReader(*args)
    rase_routes = rase_reader.get_routes_by_rase(db_helper)

    while True:
        if not delay_state:
            pass
        else:
            fiasco_handle(rase_reader, db_helper, m_fly_time)
            return
        time_worker = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
        time_delta = datetime.timedelta(hours=1, minutes=30)
        top_time_border = time_worker + time_delta
        bottom_time_border = time_worker - time_delta
        rases_in_time_diapozon = db_helper.get_rase_from_diapozon(str(top_time_border), str(bottom_time_border))
        map_exec = MapExecuter()
        for our_rase in rase_routes:
            our_map_list = map_exec.execute_by_route(route=str(our_rase[0]))
            normalize_map_list(our_map_list)
            for omp in our_map_list:
                omp.trace_reg_dict['cur_density'] = 0
            for other_rase in rases_in_time_diapozon:
                other_map_list = map_exec.execute_by_route(route=str(other_rase[6]))
                normalize_map_list(other_map_list)
                if not check_rase_time_with_group(rase_reader.time_away, \
                                                  other_rase, \
                                                  args[1], \
                                                  omp.route, \
                                                  other_map_list):
                    delay_state = True
                    breaker = True
                    break
                else:
                    breaker = False
                    fill_up_trace_short_density(our_map_list, other_map_list)
            if breaker:
                continue

            if check_route_density(our_map_list):
                delay_state = False
                t_away = datetime.datetime.strptime(rase_reader.time_away, "%Y-%m-%d %H:%M:%S")
                t_fly = datetime.timedelta(minutes=int(m_fly_time[our_rase[0]]) + 1)
                t_come = t_away + t_fly
                rase = (
                    str(t_away),
                    str(t_come),
                    str(t_fly),
                    rase_reader.company,
                    rase_reader.plane,
                    str(our_rase[0])
                )
                db_helper.insert_rase_tuple(rase)
                return
            else:
                delay_state = True