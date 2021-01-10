from pymongo import MongoClient
from os import getenv


client = MongoClient(getenv("MONGODB_URI"))
database = client.portfolio_website
main = database.main
history = database.history


# Main data includes net balance, cash balance, profits, commissions and holdings

# Returns a dictionary containing the sgd and usd value of the given field
def get_main_data(field):
    query = {"_id": "admin"}
    projection = {"_id": 0, field: 1}
    x = main.find_one(query, projection)
    return x[field]


# Sets the value of given field to new sgd and usd value given
def update_main_data(field, sgd, usd):
    query = {"_id": "admin"}
    update = {"$set": {field + ".sgd": sgd, field + ".usd": usd}}
    main.update_one(query, update)
    # Update commissions every time cash balance is updated
    if field == "cash_balance":
        update_commissions()


# Calculates commissions based on difference between net and cash balance
def update_commissions():
    net_balance = get_main_data("net_balance")
    cash_balance = get_main_data("cash_balance")
    new_sgd_commission = net_balance["sgd"] - cash_balance["sgd"]
    new_usd_commission = net_balance["usd"] - cash_balance["usd"]
    update_main_data("commissions", new_sgd_commission, new_usd_commission)


# Increment profits by given value for profits data in main collection
def update_profits(value, currency):
    query = {"_id": "admin"}
    if currency == "SGD":
        update = {"$inc": {"profits.sgd": value}} 
        main.update_one(query, update)
    else:
        update = {"$inc": {"profits.usd": value}} 
        main.update_one(query, update)


# Get all stock transaction history and returns as a list of dictionary containing
# the required details
def get_transaction_history():
    query = {"userID": "admin", "type": "transaction"}
    projection = {"_id": 0, "type": 1, "details": 1}
    return [transaction["details"] for transaction in history.find(query, projection)]


# Get all exchange and funding history and returns as a Pymongo cursor object
def get_balance_history():
    query = {"userID": "admin", "$or": [{"type": "funding"}, {"type": "exchange"}]}
    projection = {"_id": 0, "type": 1, "details": 1}
    return history.find(query, projection)


def purchase_stock(name, market_code, quantity, price, currency):
    # Log new transaction into history belonging to user with userID of admin
    details = {
        "direction": "BUY",
        "stock": name,
        "code": market_code,
        "quantity": quantity,
        "price": price,
        "currency": currency
    }
    new_transaction = {
        "userID": "admin",
        "type": "transaction",
        "details": details
    } 
    history.insert_one(new_transaction)

    # Update holdings
    value = round(quantity * price, 2)
    holdings_query = {"holdings.code": market_code}
    stock_exists = main.find_one(holdings_query)
    if not stock_exists:
        new_holding = {
            "stock": name,
            "code": market_code,
            "quantity": quantity,
            "currency": currency,
            "value": value
        }
        main.find_one_and_update({"_id": "admin"}, {"$push": {"holdings": new_holding}})

    else:
        main.find_one_and_update(holdings_query, {"$inc": {"holdings.$.quantity": quantity, "holdings.$.value": value}})

    # Decrease net balance
    trade_value = round(quantity * price, 2)
    if currency == "SGD":
        main.update_one({"_id": "admin"}, {"$inc": {"net_balance.sgd": -trade_value}})
    else:
        main.update_one({"_id": "admin"}, {"$inc": {"net_balance.usd": -trade_value}})


def sell_stock(name, market_code, quantity, price, currency):
    # Update holdings
    holdings_query = {"holdings.code": market_code}
    stock_exists = main.find_one(holdings_query)
    if stock_exists:
        stock = main.find_one(holdings_query, {"holdings.$.quantity": 1})
        current_quantity = stock["holdings"][0]["quantity"]

        # Selling of all quantity of current stocks
        if quantity == current_quantity:
            # Increment profits by difference of holding value and current trade value
            holding_value = stock["holdings"][0]["value"]
            trade_value = round(price * quantity, 2)
            update_profits(trade_value - holding_value, currency)

            # Remove stock from holdings
            update_query = {"$pull": {"holdings": {"code": market_code}}}
            main.update_one({"_id": "admin"}, update_query)

        # Partial selling of current stock, decrement by quantity
        elif quantity < current_quantity:
            main.update_one(holdings_query, {"$inc": {"holdings.$.quantity": -quantity}})

        else:
            raise Exception("Cannot sell more stocks than you hold")

    else:
        raise Exception("Cannot sell stocks not in holdings")

    # Log new transaction into transaction history if selling was successful
    details = {
        "direction": "SELL",
        "stock": name,
        "code": market_code,
        "quantity": quantity,
        "price": price,
        "currency": currency
    }
    new_transaction = {
        "userID": "admin",
        "type": "transaction",
        "details": details
    }
    history.insert_one(new_transaction)

    # Increase net balance
    trade_value = round(quantity * price, 2)
    if currency == "SGD":
        main.update_one({"_id": "admin"}, {"$inc": {"net_balance.sgd": trade_value}})
    else:
        main.update_one({"_id": "admin"}, {"$inc": {"net_balance.usd": trade_value}})


# Funds account assuming that currency is in SGD
def fund_account(date, amount):
    # Increment sgd net balance for current user with userID of admin
    query = {"_id": "admin"}
    update = {"$inc": {"net_balance.sgd": amount}}
    main.update_one(query, update)

    # Add funding history to history belonging to user with userID of admin
    details = {
        "date": date,
        "amount": amount
    }
    new_funding = {
        "userID": "admin",
        "type": "funding",
        "details": details
    }
    history.insert_one(new_funding)


# Exchanges currency for only two direction, SGD to USD or USD to SGD
def exchange_currency(date, direction, sgd, usd):
    # Increase net balance usd and decrease net balance sgd
    if direction == "SGD to USD":
        query = {"_id": "admin"}
        update = {"$inc": {"net_balance.sgd": -sgd, "net_balance.usd": usd}}
        main.update(query, update)
    # Increase net balance sgd and decrease net balance usd
    else:
        query = {"_id": "admin"}
        update = {"$inc": {"net_balance.sgd": sgd, "net_balance.usd": -usd}}
        main.update(query, update)

    # Add new exchange to history belonging to user with userID of admin
    details = {
        "date": date,
        "direction": direction,
        "sgd" : sgd,
        "usd": usd
    }
    new_exchange = {
        "userID": "admin",
        "type": "exchange",
        "details": details
    }
    history.insert_one(new_exchange)