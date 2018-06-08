import pymysql

connection = pymysql.connect(host="127.0.0.1",
							 user="root",
					 		 password="root",
					 		 db="diplom_rase",
							)

try:
	with connection.cursor() as cur:
		sql = "SELECT * FROM rase"
		cur.execute(sql)
		result = cur.fetchall()
		print("RESULT: ", result)
except:
	print("Error")
	connection.close()
else:
	connection.close()
