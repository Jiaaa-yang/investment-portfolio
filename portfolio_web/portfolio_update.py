from pymongo import MongoClient
from os import getenv


client = MongoClient(getenv("MONGODB_URI"))
database = client.portfolio_website
main = database.main
history = database.history


def read_portfolio():
    # Returns the main portfolio with an admin id
    return main.find_one({"_id": "admin"})


def get_history(required_type):
    query = {"userID": "admin", "type": required_type}
    return history.find_one(query)["history"] 


def update_account_balance(sgd_balance, usd_balance):
    main.update_one({"_id": "admin"}, 
    {"$set": {"sgd_balance": sgd_balance, "usd_balance": usd_balance}})


def purchase_stock(name, market_code, quantity, price, currency):
    new_transcation = {
        "direction": "BUY",
        "stock": name,
        "code": market_code,
        "quantity": quantity,
        "price": price,
        "currency": currency
    }
    # Log new transaction into transaction history
    transaction_query = {"userID": "admin", "type": "transaction"}
    transcation_update = {"$push": {"history": new_transcation}}
    history.update_one(transaction_query, transcation_update)

    # Update holdings
    holdings_query = {"holdings.code": market_code}
    stock_exists = main.find_one(holdings_query)
    if not stock_exists:
        new_holding = {
            "stock": name,
            "code": market_code,
            "quantity": quantity
        }
        main.find_one_and_update({"_id": "admin"}, {"$push": {"holdings": new_holding}})

    else:
        main.find_one_and_update(holdings_query, {"$inc": {"holdings.$.quantity": quantity}})


def sell_stock(name, market_code, quantity, price, currency):
    new_transcation = {
        "direction": "SELL",
        "stock": name,
        "code": market_code,
        "quantity": quantity,
        "price": price,
        "currency": currency
    }
    # Update holdings
    holdings_query = {"holdings.code": market_code}
    stock_exists = main.find_one(holdings_query)
    if stock_exists:
        stock = main.find_one({"holdings.code": market_code}, {"holdings.$.quantity":1})
        current_quantity = stock["holdings"][0]["quantity"]

        # Selling of all quantity of the current stock, remove from holdings
        if quantity == current_quantity:
            update_query = {"$pull": {"holdings": {"code": market_code}}}
            main.update_one({"_id": "admin"}, update_query)

        # Partial selling of current stock, decrement by quantity
        elif quantity < current_quantity:
            main.find_one_and_update(holdings_query, {"$inc": {"holdings.$.quantity": -quantity}})

        else:
            raise Exception("Cannot sell more stocks than you hold")

    else:
        raise Exception("Cannot sell stocks not in holdings")

    # Log new transaction into transaction history
    transaction_query = {"userID": "admin", "type": "transaction"}
    transcation_update = {"$push": {"history": new_transcation}}
    history.update_one(transaction_query, transcation_update)


def fund_account(date, amount):
    new_funding = {
        "date": date,
        "currency": "SGD",
        "amount": amount
    }
    funding_query = {"userID": "admin", "type": "funding"}
    funding_update = {"$push": {"history": new_funding}}
    history.update_one(funding_query, funding_update)