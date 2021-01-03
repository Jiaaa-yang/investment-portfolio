import json
data_file = "data.json"

class MyPortfolio():
    def __init__(self, sgd_balance=0, usd_balance=0, 
                holdings=[], funding_history=[], transaction_history=[]):
        self.sgd_balance = sgd_balance
        self.usd_balance = usd_balance
        self.holdings = holdings  
        self.funding_history = funding_history 
        self.transaction_history = transaction_history 


    def update_balance(self, currency, value):
        if currency == "SGD":
            self.sgd_balance = value
        elif currency == "USD":
            self.usd_balance = value
        else:
            raise Exception("Currency entered is not USD or SGD")


    def purchase_stock(self, stock_name, market_code, quantity, price, currency):
        buy_details = {
            "direction": "BUY",
            "stock": stock_name,
            "code": market_code,
            "quantity": quantity,
            "price": price,
            "currency": currency
        }

        # Append buy history
        self.transaction_history.append(buy_details)

        for holding in self.holdings:
            #  Current stock exists in holdings
            if holding["code"] == market_code:
                holding["quantity"] += quantity
                return

        # Stock does not exist, append to holdings
        new_stock = {
            "stock": stock_name,
            "code": market_code,
            "quantity": quantity
        }
        self.holdings.append(new_stock)


    def sell_stock(self, stock_name, market_code, quantity, price, currency):
        sell_details = {
            "direction": "SELL",
            "stock": stock_name,
            "code": market_code,
            "quantity": quantity,
            "price": price,
            "currency": currency
        }

        for holding in self.holdings:
            #  Current stock exists in holdings
            if holding["code"] == market_code:
                holding["quantity"] -= quantity
                if holding["quantity"] == 0:
                    self.holdings.remove(holding)
                self.transaction_history.append(sell_details)
                return
        
        # No stocks exist to sell
        raise Exception("Cannot sell stocks that does not exist in holdings")

    
    def fund_account(self, date, amount):
        funding = {
            "date": date,
            "currency": "SGD",
            "amount": amount
        }
        self.funding_history.append(funding)

    
    def save(self):
        with open(data_file, "w") as file:
            json.dump(self.__dict__, file, indent=4)


def load_portfolio():
    with open(data_file, "r") as file:
        data = json.load(file)
        return MyPortfolio(**data)