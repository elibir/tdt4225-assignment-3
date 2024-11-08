from pprint import pprint 
from DbConnector import DbConnector
import os
from datetime import datetime
from dateutil.parser import parse

class ExampleProgram:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset/')  # Ensures that os methods has this file's location as its root

    def create_coll(self, collection_name):
        collection = self.db.create_collection(collection_name)    
        print('Created collection: ', collection)
        
    def fetch_documents(self, collection_name, limit):
        collection = self.db[collection_name]
        documents = collection.find().limit(limit)
        for doc in documents: 
            pprint(doc)

    def drop_coll(self, collection_name):
        collection = self.db[collection_name]
        collection.drop()

    def show_coll(self):
        collections = self.client['geolife'].list_collection_names()
        print(collections)
         
    def insert_data(self):
        user_ids = os.listdir(self.base_path + "Data")
        with open(self.base_path + "labeled_ids.txt", 'r') as f:
            labeled_ids = {line.strip() for line in f}

        activity_id = 1 # start the id at 1 and then increment    
        for user_id in user_ids:
            collection = self.db["user"]
            has_labels = user_id in labeled_ids
            collection.insert_one({
                "_id": user_id,
                "has_labels": has_labels
            })
            activity_id = self.filter_and_insert_activities(activity_id, user_id, has_labels)
            
        print("All data inserted successfully.")
        
    def insert_activity(self, activity_id, user_id, transportation_mode, start_time, end_time, trackpoint_ids):
        self.db.activity.insert_one({
            "_id": activity_id,
            "transportation_mode": transportation_mode,
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "trackpoints": trackpoint_ids
        })
        
    def filter_and_insert_activities(self, activity_id, user_id, has_labels):
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

            formatted_trackpoints = self.prepare_trackpoints(activity_id, trackpoints)
            # Insert the trackpoints and retrieve the inserted IDs
            result = self.db.trackpoint.insert_many(formatted_trackpoints)
            trackpoint_ids = result.inserted_ids    
            self.insert_activity(activity_id, user_id, transportation_mode, start_time, end_time, trackpoint_ids)
            activity_id += 1
        print("Finished inserting activities for user: ", user_id)
        return activity_id       
    
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
    
    def prepare_trackpoints(self, activity_id, trackpoints):
        formatted_trackpoints = []
        for trackpoint in trackpoints:
            latitude = float(trackpoint[0])
            longitude = float(trackpoint[1])
            altitude = int(float(trackpoint[3])) # truncate to get same results as MySql assignment
            date_days = float(trackpoint[4])
            # Merge date and hour into a single datetime object
            date_time = parse(trackpoint[5] + " " + trackpoint[6])
            formatted_trackpoints.append(
                {"lat": latitude,
                 "lon": longitude,
                 "altitude": altitude,
                 "date_days": date_days,
                 "date_time": date_time,
                 "activity_id": activity_id
                }
            )
        return formatted_trackpoints  

def main():
    program = None
    try:
        program = ExampleProgram()
        program.drop_coll("user")
        program.drop_coll("activity")
        program.drop_coll("trackpoint")
        program.create_coll("user")
        program.create_coll("activity")
        program.create_coll("trackpoint")
        program.insert_data()
        program.fetch_documents(collection_name="user", limit=10)
        program.fetch_documents(collection_name="activity", limit=1)
        program.fetch_documents(collection_name="trackpoint", limit=10)
        program.show_coll()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
