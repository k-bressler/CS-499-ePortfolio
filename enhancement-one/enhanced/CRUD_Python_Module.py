# CS 499 Capstone Project
#Kaitlin Bressler

#import libraries
from pymongo import MongoClient 
from bson.objectid import ObjectId 
from pymongo.errors import PyMongoError

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, USER=None, PASS=None, HOST='localhost', PORT=27017, DB='AAC', COL='animals'):
        # Initialize local MongoDB connection
        self.client = MongoClient(HOST, PORT)
        self.database = self.client[DB]
        self.collection = self.database[COL]

    ##########################################################
    #METHOD: next record number
    #a method to return the next available record number for use in the create method
    ##########################################################
    
    def next_record_number(self):
        
        try: 
            #find the record with the highest rec num
            last_record = self.collection.find_one(
                {"rec_num": {"$exists": True, "$ne": None}},
                sort=[("rec_num", -1)]
            )

            #if no rec num exists, begin numbering after the imported records
            if last_record is None:
                return self.collection.count_documents({}) + 1
        
            return int(last_record["rec_num"]) +1
    
        except Exception as e:
            print("Error getting next record number:", e)
            return None
            
    ##########################################################
    #CREATE (insert new document)
    #insert document, return if successful, else false
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

        except PyMongoError as e: 
            print("Insert failed", e) 
            return False


    ##########################################################
    #READ (query documents)
    #query documents using key/value lookup
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
    #UPDATE (modify document)
    #Modifies document(s) that match query
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
    
        except PyMongoError as e:
            print("Update failed", e)
            return 0
    
    ##########################################################
    #DELETE (delete document)
    #remove document(s) that match query
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
    