from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv


load_dotenv()
client = MongoClient(getenv("MONGODB_URI"))
database = client.portfolio_website
main = database.main
history = database.history


def create_database():
    main_document = {
        "_id": "admin",
        "net_balance": {
            "sgd": 0,
            "usd": 0
        },
        "cash_balance": {
            "sgd": 0,
            "usd": 0
        },
        "profits": {
            "sgd": 0,
            "usd": 0
        },
        "commissions": {
            "sgd": 0,
            "usd": 0
        },
        "holdings": []
    }
    main.insert_one(main_document)


def clear_database():
    main.delete_many({})
    history.delete_many({})