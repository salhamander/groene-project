import mysql.connector
import pickle as p

db = mysql.connector.connect(
  host='localhost',
  user='root',
  passwd='',
  database='actualiteitenprogrammas'
)

print(db)

cur = db.cursor()

# Use all the SQL you like
cur.execute("""
	SELECT * FROM actualiteitenprogrammas_tweets
	WHERE text LIKE '%islam%'

	""")

# print all the first cell of all the rows
results = cur.fetchall()
# print(results)
# for x in results:
# 	print(x)
db.close()

p.dump(results, open('islam_tweets.p', 'wb'))