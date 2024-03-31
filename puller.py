import requests
import pymysql
import config

class Database:
    def __init__(self, host, user, password, database):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cur = self.connection.cursor()

    def create_table(self, query):
        try:
            self.cur.execute(query)
        except Exception as e:
            print(f"Error creating table: {query}")
            print(f"Error message: {str(e)}")

    def insert_data(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        self.cur.execute(query, values)
        self.connection.commit()

    def insert_mods_data(self, table_name, data, char_base_id):
        values = ", ".join([f"`{field_name}`='{field_value}'" for field_name, field_value in data.items()])
        query = f"UPDATE {table_name} SET {values} WHERE char_id = '{char_base_id}'"
        self.cur.execute(query)
        self.connection.commit()  

def pull_data_from_api(api_url, table_name, columns_mapping):
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        for record in data:
            formatted_data = {columns_mapping[key]: record[key] for key in columns_mapping}
            db.insert_data(table_name, formatted_data)
    else:
        print(f"Error fetching data from API for {table_name}")

def get_modules():
    response = requests.get(config.chars_api)
    data = response.json()
    base_ids = [item['base_id'] for item in data]

    for char_base_id in base_ids:
        url = config.mods_api.format(char_id=char_base_id)
        response = requests.get(url)
        mods_data = response.json()['best_mod_slots']
        sets_data = response.json()['best_mod_sets']
        mods = {}

        for _, value in mods_data.items():
            name = value['name']
            stats = value['data']['stats']
            max_stat_key = max(stats, key=stats.get)
            mods[name.lower()] = max_stat_key
        
        if len(sets_data)>0:
            best_sets = max(sets_data, key=lambda x: x["count"])
            sets = ' '.join(best_sets["sets"])
            mods['sets'] = sets
                
        if len(mods)>0:
            db.insert_mods_data('chars', mods, char_base_id) 

db = Database(config.host, config.user, config.password, config.database)

for table_query in config.tables:
    db.create_table(table_query)

pull_data_from_api(config.stats_api, 'stats', {'stat_name': 'stat_name', 'stat_id': 'stat_id'})
pull_data_from_api(config.chars_api, 'chars', {'name': 'char_name', 'base_id': 'char_id'})
get_modules()

db.connection.close()
