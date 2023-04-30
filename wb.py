import mysql.connector
import requests
from bs4 import BeautifulSoup

# define MySQL connection parameters
host = '#'
user = '#'
password = '#'
database = '#'

# define headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Cookie": "PC_TOKEN=6f9e52b01d; SUB=_2AkMTEHgBf8NxqwJRmfoWym7lb4x_zwDEieKlTInaJRMxHRl-yT9yqkJftRB6OJBW7bJos5inx_6hCthM6TJ76FwYQ7ZW; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WF_1TillyEYhAXNb7JWrHKZ; login_sid_t=625275c0db6329a79d731e8eed375f1b; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=8355534746098.403.1682765625982; SINAGLOBAL=8355534746098.403.1682765625982; ULV=1682765625991:1:1:1:8355534746098.403.1682765625982:"
}

# create a MySQL connection
conn = mysql.connector.connect(host=host, user=user, password=password, database=database)

# create a cursor object
cursor = conn.cursor()

# check if the table already exists
table_exists = False
cursor.execute("SHOW TABLES")
for table in cursor:
    if table[0] == 'weibo_hot':
        table_exists = True
        break

# create the table if it doesn't exist
if not table_exists:
    cursor.execute("""
        CREATE TABLE weibo_hot (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hot_rank int,
            hot_title VARCHAR(255),
            hot_index VARCHAR(10),
            hot_degree VARCHAR(50),
            hot_link VARCHAR(255)
        )""")
    conn.commit()
else:
    # truncate the table if it exists
    cursor.execute("TRUNCATE TABLE weibo_hot")
    conn.commit()

# get the HTML content
url = 'https://s.weibo.com/top/summary'
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# extract the ranking items and save them to MySQL
items = soup.select('tbody tr')
...
for item in items:
    # 判断是否为置顶
    if item.select('.icon-top'):
        hot_rank = 0
    else:
        try:
            hot_rank_str = item.select('.td-01.ranktop')[0].get_text().strip()
            hot_rank = int(''.join(filter(str.isdigit, hot_rank_str)))
        except (IndexError, ValueError):
            continue
    hot_title = item.select('.td-02 a')[0].get_text().strip()
    hot_link = "https://s.weibo.com" + item.select('.td-02 a')[0]['href']

    try:
        hot_index = item.select('td.td-02 span')[0].get_text().strip()
    except IndexError:
        hot_index = ""

    hot_degree_nodes = item.select('td.td-03 i')
    hot_degree = hot_degree_nodes[0].get_text().strip() if hot_degree_nodes else ""

    cursor.execute("""
        INSERT INTO weibo_hot (hot_rank, hot_title, hot_index, hot_degree, hot_link) 
        VALUES (%s, %s, %s, %s, %s)
    """, (hot_rank, hot_title, hot_index, hot_degree, hot_link))
    conn.commit()
