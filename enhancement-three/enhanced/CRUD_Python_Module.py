# CS 499 Capstone Project
#Kaitlin Bressler

# Import libraries
from pymongo import MongoClient 
from pymongo.errors import PyMongoError, OperationFailure, WriteError

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, USER=None, PASS=None, HOST='localhost', PORT=27017, DB='AAC', COL='animals'):

        # Initialize local MongoDB connection
        self.client = MongoClient(HOST, PORT)
        self.database = self.client[DB]
        self.collection = self.database[COL]

    ##########################################################
    # METHOD: Schema Validation
    # Adds MongoDB validation rules to protect records
    ##########################################################

    def configure_schema_validation(self):

        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "animal_type", "breed", "age_upon_outcome_in_weeks", "sex_upon_outcome"],
                "properties": {
                    "rec_num": {"bsonType": ["int", "long"]},
                    "name": {"bsonType": "string", "minLength": 1, "description": "Animal name must be a string"},
                    "animal_type": {"bsonType": "string", "minLength": 1, "description": "Animal type must be a string"},
                    "breed": {"bsonType": "string", "minLength": 1, "description": "Breed must be a string"},
                    "age_upon_outcome_in_weeks": {"bsonType": ["int", "long", "double"], "minimum": 0, "description": "Age must be a non-negative number"},
                    "sex_upon_outcome": {"enum": ["Intact Male", "Intact Female", "Neutered Male", "Spayed Female", "Unknown"], "description": "Sex must contain an approved value"}
                }
            }
        }

        try:
            self.database.command({"collMod": self.collection.name, "validator": validator, "validationLevel": "strict", "validationAction": "error"})

            print("Schema validation configured successfully.")
            return True

        except OperationFailure as e:
            print("Error configuring schema validation:", e)
            return False

    ##########################################################
    # METHOD: Next Record Number
    # Returns the next available record number for new records
    ##########################################################
    
    def next_record_number(self):
        
        try: 
            # Find the record with the highest rec num
            last_record = self.collection.find_one(
                {"rec_num": {"$exists": True, "$ne": None}},
                sort=[("rec_num", -1)]
            )

            # If no rec num exists, begin numbering after the imported records
            if last_record is None:
                return self.collection.count_documents({}) + 1
        
            return int(last_record["rec_num"]) + 1
    
        except Exception as e:
            print("Error getting next record number:", e)
            return None
            
    ##########################################################
    # CREATE
    # Inserts a new record
    ##########################################################
    
    def create(self, data):
        
        if data is None: 
            raise Exception("Nothing to save, because data parameter is empty") 
            
        try: 
            record_number = self.next_record_number()

            if record_number is None:
                print("Insert failed: could not generate record number")
                return False
            
            data["rec_num"] = record_number

            result = self.collection.insert_one(data)

            return result.inserted_id is not None

        # Handle write errors, including validation errors  
        except WriteError as e:
            if e.code == 121:
                print("Insert failed: record did not meet validation requirements")
            else:
                print("Insert failed:", e)
            return False

        except PyMongoError as e:
            print("Database error during insert:", e)
            return False


    ##########################################################
    # READ
    # Query records using key/value lookup
    ##########################################################
    
    def read(self, query):
        
        try:
            cursor = self.collection.find(query)
            results = [doc for doc in cursor]
            return results
        
        except PyMongoError as e:
            print("Query failed", e)
            return []
    
    ##########################################################
    # UPDATE 
    # Modifies record(s) that match query
    ##########################################################
    
    def update(self, query, new_values, many=False):
        
        if query is None or new_values is None:
            raise Exception("Query & update values cannot be empty")
            
        try:
            if many:
                result = self.collection.update_many(query, {"$set": new_values})
            else:
                result = self.collection.update_one(query, {"$set": new_values})
                
            return result.modified_count
    
        # Handle write errors, including validation errors  
        except WriteError as e:
            if e.code == 121:
                print("Update failed: record did not meet validation requirements")
            else:
                print("Update failed:", e)
            return 0

        except PyMongoError as e:
            print("Database error during update:", e)
            return 0
    
    ##########################################################
    # DELETE
    # Removes record(s) that match query
    ##########################################################
    
    def delete(self, query, many=False):
        
        if query is None:
            raise Exception("Query parameter cannot be empty")
            
        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
                
            return result.deleted_count
        
        except PyMongoError as e:
            print("Delete failed", e)
            return 0
    