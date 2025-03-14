from pymongo import MongoClient






if __name__ == "__main__":
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client('my_db')
    collection = db['orders']

    data = collection.find({"department": "HR"})

    print(list(data))
    exit()
    # documents = [
    #     {'name': 'John Doe', 'age': 30, 'department': 'Marketing'},
    #     {'name': 'Jane Smith', 'age': 35, 'department': 'Finance'},
    #     {'name': 'Alice Johnson', 'age': 25, 'department': 'HR'}
    # ]
    # insert_result = db.insert_many(documents)


    condition = {
        'department' : 'Marketing'
    }

    upgrade = {
        "$set" : {
            "department": 'Sales',
        }
    }
    collection.delete_one(condition)
