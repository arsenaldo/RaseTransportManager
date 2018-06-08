from DBhelper import DBhelper
from TraceRegionMaper import TraceRegionMaper
import copy


class MapExecuter(DBhelper):
    def __init__(self,
                 host='localhost',
                 user='root',
                 password='root',
                 db='diplom_rase'):
        super(MapExecuter, self).__init__()

    def execute_by_route(self, route):
        print("BRRREEEEE")
        my_list = []
        try:
            with self.connection.cursor() as cursor:
                sql = "select p1.id as p1_id, \
	   				   p1.name, p2.id as p2_id, p2.name,\
	   				   trace_short.id as TRACE_ID, \
	   				   region.name as region_name, region.density as region_density, \
	   				   route \
					   from place as p1 \
					   JOIN trace_short ON p1.id = trace_short.place_from \
					   JOIN place as p2 ON p2.id = trace_short.place_to \
					   JOIN relation ON trace_short.id = relation.trace \
					   JOIN region ON relation.region = region.id \
					   WHERE trace_short.route = %s \
					   ORDER BY route, trace_short.id, region.name; "
                cursor.execute(sql, (route))
                result = cursor.fetchall()
                for res in result:
                    trace_reg_maper = TraceRegionMaper(res)
                    my_list.append(copy.deepcopy(trace_reg_maper))
        except:
            print("GET error")
        return my_list
