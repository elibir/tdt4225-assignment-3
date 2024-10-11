from DbConnector import DbConnector
from tabulate import tabulate
import mysql.connector
from mysql.connector import errorcode
from tables import TABLES
import os
from datetime import datetime
from dateutil.parser import parse


class DbCreator:

    def __init__(self):
        self.db_connector = DbConnector()
        self.connection = self.db_connector.db_connection
        self.cursor = self.db_connector.cursor
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset/')  # Ensures that os methods has this file's location as its root
        
    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))
        
    def fetch_data(self, table_name):
        query = "SELECT * FROM %s"
        self.cursor.execute(query % table_name)
        rows = self.cursor.fetchmany(10)
        # print("Data from table %s, raw format:" % table_name)
        # print(rows)
        
        # Using tabulate to show the table in a nice way
        print("Data from table %s, tabulated:" % table_name)
        print(tabulate(rows, headers=self.cursor.column_names))
        return rows
    
    def drop_table(self, table_name):
        print("Dropping table %s..." % table_name)
        query = "DROP TABLE %s"
        self.cursor.execute(query % table_name)    
     
    def create_tables(self):   
        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print("Creating table {}: ".format(table_name), end='')
                self.cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")
                
        self.connection.commit()

    def empty_table(self, table_name):
        query = f"DELETE FROM `{table_name}`"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Table `{table_name}` has been emptied.")
        except Exception as e:
            print(f"An error occurred while emptying the table `{table_name}`: {e}")
        
    def insert_userdata(self):
        user_ids = os.listdir(self.base_path + "Data")
        with open(self.base_path + "labeled_ids.txt", 'r') as f:
            labeled_ids = {line.strip() for line in f}

        for user_id in user_ids:
            has_labels = user_id in labeled_ids
            try:
                query = "INSERT INTO `User` (id, has_labels) VALUES (%s, %s)"
                self.cursor.execute(query, (user_id, has_labels))
            except mysql.connector.Error as err:
                print(f"Error inserting user {user_id}: {err.msg}")

        self.connection.commit()
        print("User data inserted successfully.")
        
    def insert_activity(self, user_id, transportation_mode, start_date_time, end_date_time):
        query = "INSERT INTO Activity (user_id, transportation_mode, start_date_time, end_date_time) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (user_id, transportation_mode, start_date_time, end_date_time))
        return self.cursor.lastrowid
        
    def prepare_trackpoints(self, activity_id, trackpoints):
        formatted_trackpoints = []
        for trackpoint in trackpoints:
            latitude = trackpoint[0]
            longitude = trackpoint[1]
            altitude = trackpoint[3]
            date_days = trackpoint[4]
            # Merge date and hour into a single datetime object
            date_time = parse(trackpoint[5] + " " + trackpoint[6])
            formatted_trackpoints.append((activity_id, latitude, longitude, altitude, date_days, date_time))
        return formatted_trackpoints
        
    def insert_all_trackpoints(self, all_formatted_trackpoints, batch_size=400000):
        query = """
            INSERT INTO TrackPoint (activity_id, lat, lon, altitude, date_days, date_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        total_trackpoints = len(all_formatted_trackpoints)
        for i in range(0, total_trackpoints, batch_size):
            batch = all_formatted_trackpoints[i:i+batch_size]
            try:
                self.cursor.executemany(query, batch)
                self.connection.commit()
            except mysql.connector.Error as err:
                print(f"Error inserting batch {i // batch_size}: {err}")
            print("Finished inserting ", i + len(batch) , "trackpoints.")
        
    def filter_and_insert_activities(self):
        self.cursor.execute("SELECT * FROM User")
        user_tuples = self.cursor.fetchall()
        all_formatted_trackpoints = []
        for user_id, has_labels in user_tuples:
            activity_files = os.listdir(self.base_path + "Data/" + user_id + "/Trajectory")
            if len(activity_files) == 0: raise FileNotFoundError("No activity files found for user", user_id)
            for plt_file in activity_files:
                trackpoints = self.read_plt(self.base_path + "Data/" + user_id + "/Trajectory/" + plt_file)
                if trackpoints == None: continue
                start_time = datetime.strptime(trackpoints[0][5] + " " + trackpoints[0][6], "%Y-%m-%d %H:%M:%S") 
                end_time = datetime.strptime(trackpoints[-1][5] + " " + trackpoints[-1][6], "%Y-%m-%d %H:%M:%S")
                transportation_mode = None
                if has_labels == 1:
                    label_dict = self.read_labels(self.base_path + "Data/" + user_id + "/labels.txt")
                    transportation_mode = label_dict.get((start_time, end_time))
                activity_id = self.insert_activity(user_id, transportation_mode, start_time, end_time)
                # Prepare trackpoints but do not insert yet
                formatted_trackpoints = self.prepare_trackpoints(activity_id, trackpoints)
                all_formatted_trackpoints.extend(formatted_trackpoints)
            print("Finished processing activities for user:", user_id)
        # Insert all trackpoints at once
        print("Inserting trackpoints...")
        self.insert_all_trackpoints(all_formatted_trackpoints)
        self.connection.commit()
        print("Finished inserting all trackpoints")
                
    def read_plt(self, file_path):
        data = []
        with open(file_path, 'r') as file:
            for _ in range(6):  # Skip header lines
                next(file)
            for line in file:
                if len(data) > 2500:
                    return None  # Skip files with more than 2500 trackpoints
                data.append(line.strip().split(','))
        return data
    
    def read_labels(self, file_path):
        label_dict = {}
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines[1:]:  # Skip the header
            label = line.strip().split("\t")
            start_time = datetime.strptime(label[0], "%Y/%m/%d %H:%M:%S")
            end_time = datetime.strptime(label[1], "%Y/%m/%d %H:%M:%S")
            transportation_mode = label[2]  
            # Store directly in dictionary with (start_time, end_time) as key
            label_dict[(start_time, end_time)] = transportation_mode
        return label_dict          
                      
def main():
    program = None
    try:
        program = DbCreator()
        program.create_tables()
        program.insert_userdata()
        program.filter_and_insert_activities()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.db_connector.close_connection()

if __name__ == '__main__':
    main()
    