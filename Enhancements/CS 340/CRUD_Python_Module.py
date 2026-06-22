# Example Python Code to Insert a Document 

from pymongo import MongoClient, ReturnDocument 
from bson.objectid import ObjectId 

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, username, password): 
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections. This is hard-wired to use the aac 
        # database, the animals collection, and the aac user. 
        # 
        # You must edit the password below for your environment. 
        # 
        # Connection Variables 
        # 
        # USER = 'aacuser' 
        # PASS = 'snhupassword' 
        USER = username
        PASS = password
        HOST = 'localhost' 
        PORT = 27017 
        DB = 'aac' 
        COL = 'animals' 
        # 
        # Initialize Connection 
        # 
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT)) 
        self.database = self.client['%s' % (DB)] 
        self.collection = self.database['%s' % (COL)]
        self.create_indexes()
    
    def create_indexes(self):
        self.database.animals.create_index("animal_type")
        self.database.animals.create_index("breed")
        self.database.animals.create_index("sex_upon_outcome")
        self.database.animals.create_index("outcome_type")

    # Create a method to return the next available record number for use in the create method
    #Generates the next available record number
    def return_record_number(self):
        db_query = self.database.counters.find_one_and_update(
            {"_id": "animals"},
            #Automatically increment sequence number
            {"$inc": {"seq": 1}},
            return_document=ReturnDocument.AFTER,
            upsert= True
        )
        return db_query["seq"]
        
    
    # Complete this create method to implement the C in CRUD.
    #Creates new record witin animals
    #Assigns a unique record number

    
    def create(self, data):
        if data is not None:
            data["rec_num"] = self.return_record_number()
            self.database.animals.insert_one(data) # data should be dictionary
            return True
        else: 
            # raise Exception("Nothing to save, because data parameter is empty")
            return False

    # Create method to implement the R in CRUD.
    def read(self, data, projection=None):
        # If no query is provided, return all records
        if data is None or data == {}:
            query = {}

        # Verifies inputted data is correct type
        elif not isinstance(data, dict):
            raise Exception("Invalid data type")

        else:
            query = {}

            for key, value in data.items():
                # Verifies that key and/or value is not null
                if key is None or value is None:
                    return []

                # Verifies key is correct type
                if not isinstance(key, str):
                    return []

                # Verifies key is not empty
                if key.isspace() or key == "":
                    return []

                # Verifies value is correct type and normalizes value
                if isinstance(value, str):
                    cleaned = value.strip()

                    if cleaned == "":
                        return []

                    query[key] = cleaned

                else:
                    query[key] = value

        # Default projection removes MongoDB ObjectId
        if projection is None:
            projection = {"_id": 0}

        # Returns a list with matching results of query
        results = list(self.database.animals.find(query, projection))
        return results
        
    def update(self, old_data, data):
        if data is None:
            raise Exception("Input is empty")
        #Verifies inputted data is correct type
        elif not isinstance(data, dict):
            raise Exception("Invalid data type")
        #Verifies inputted data isn't empty
        elif len(data) == 0:
            raise Exception("Dictionary is empty")
        query = {}
        
        for key,value in data.items():
            #Verifies that key and/or value is not null
            if key == None or value == None:
                raise Exception("Null Key or Value")
            #Verifies key is correct type
            if not isinstance(key, str):
                raise Exception("Invalid Key Type")
            #Verifies key is not empty
            if key.isspace() or key == "":
                raise Exception("Invalid Key")
            #Verifies value is correct type and normalizes value
            if isinstance(value, str):
                cleaned = value.strip().lower()
                if cleaned == "":
                    raise Exception("Invalid Value")
                query[key] = cleaned
            #Verifies value is not empty
            if value.isspace() or value == "":
                raise Exception("Invalid Value")
        data = {"$set": data}
        results = self.database.animals.update_one(old_data, data)
        
        return f'{results.modified_count} documents updated.'
        
    
    def delete(self, data):
        if data is None:
            raise Exception("Input is empty")
        #Verifies inputted data is correct type
        elif not isinstance(data, dict):
            raise Exception("Invalid data type")
        #Verifies inputted data isn't empty
        elif len(data) == 0:
            raise Exception("Dictionary is empty")
        query = {}
        
        for key,value in data.items():
            #Verifies that key and/or value is not null
            if key == None or value == None:
                raise Exception("Null Key or Value")
            #Verifies key is correct type
            if not isinstance(key, str):
                raise Exception("Invalid Key Type")
            #Verifies key is not empty
            if key.isspace() or key == "":
                raise Exception("Invalid Key")
            #Verifies value is correct type and normalizes value
            if isinstance(value, str):
                cleaned = value.strip().lower()
                if cleaned == "":
                    raise Exception("Invalid Value")
                query[key] = cleaned
            #Verifies value is not empty
            if value.isspace() or value == "":
                raise Exception("Invalid Value")
        result = self.database.animals.delete_many(data)
        
        return f"{result.deleted_count} document(s) removed"
    
    def breed_counts(self, query=None):
        try:
            if query is None:
                query = {}

            pipeline = [
                {"$match": query},
                {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]

            return list(self.database.animals.aggregate(pipeline))

        except Exception as e:
            print("An exception occurred while calculating breed counts:", e)
            return []


    def outcome_counts(self, query=None):
        try:
            if query is None:
                query = {}

            pipeline = [
                {"$match": query},
                {"$group": {"_id": "$outcome_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]

            return list(self.database.animals.aggregate(pipeline))

        except Exception as e:
            print("An exception occurred while calculating outcome counts:", e)
            return []


    def rescue_category_totals(self):
        try:
            pipeline = [
                {
                    "$facet": {
                        "water_rescue": [
                            {
                                "$match": {
                                    "animal_type": "Dog",
                                    "breed": {
                                        "$in": [
                                            "Labrador Retriever Mix",
                                            "Chesapeake Bay Retriever",
                                            "Newfoundland"
                                        ]
                                    },
                                    "sex_upon_outcome": "Intact Female",
                                    "age_upon_outcome_in_weeks": {
                                        "$gte": 26,
                                        "$lte": 156
                                    }
                                }
                            },
                            {"$count": "count"}
                        ],
                        "mountain_rescue": [
                            {
                                "$match": {
                                    "animal_type": "Dog",
                                    "breed": {
                                        "$in": [
                                            "German Shepherd",
                                            "Alaskan Malamute",
                                            "Old English Sheepdog",
                                            "Siberian Husky",
                                            "Rottweiler"
                                        ]
                                    },
                                    "sex_upon_outcome": "Intact Male",
                                    "age_upon_outcome_in_weeks": {
                                        "$gte": 26,
                                        "$lte": 156
                                    }
                                }
                            },
                            {"$count": "count"}
                        ],
                        "disaster_rescue": [
                            {
                                "$match": {
                                    "animal_type": "Dog",
                                    "breed": {
                                        "$in": [
                                            "Doberman Pinscher",
                                            "German Shepherd",
                                            "Golden Retriever",
                                            "Bloodhound",
                                            "Rottweiler"
                                        ]
                                    },
                                    "sex_upon_outcome": "Intact Male",
                                    "age_upon_outcome_in_weeks": {
                                        "$gte": 20,
                                        "$lte": 300
                                    }
                                }
                            },
                            {"$count": "count"}
                        ]
                    }
                }
            ]

            return list(self.database.animals.aggregate(pipeline))

        except Exception as e:
            print("An exception occurred while calculating rescue category totals:", e)
            return []