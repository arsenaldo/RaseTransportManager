class TraceRegionMaper:
	def __init__(self, sql_row):
		self.trace_reg_dict = {}
		self.trace_reg_dict['place_from_id'] = sql_row[0]
		self.trace_reg_dict['place_from_name'] = sql_row[1]
		self.trace_reg_dict['place_to_id'] = sql_row[2]
		self.trace_reg_dict['place_to_name'] = sql_row[3]
		self.trace_reg_dict['trace_id'] = sql_row[4]
		self.trace_reg_dict['region_name'] = sql_row[5]
		self.trace_reg_dict['region_density'] = sql_row[6]
		self.trace_reg_dict['route'] = sql_row[7]	

	def __str__(self):
		return str(self.trace_reg_dict)

	@property
	def place_from_id(self):
		return self.trace_reg_dict['place_from_id']

	@property
	def place_from_name(self):
		return self.trace_reg_dict['place_from_name']

	@property
	def place_to_id(self):
		return self.trace_reg_dict['place_to_id']

	@property
	def place_to_name(self):
		return self.trace_reg_dict['place_to_name']

	@property
	def trace_id(self):
		return self.trace_reg_dict['trace_id']

	@property
	def region_name(self):
		return self.trace_reg_dict['region_name']

	@property
	def region_density(self):
		return self.trace_reg_dict['region_density']

	@property
	def route(self):
		return self.trace_reg_dict['route']
