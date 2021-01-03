from flask import Flask, url_for, render_template, request, redirect
from portfolio import load_portfolio
from datetime import datetime


app = Flask(__name__)
current_date = datetime.now().strftime("%d %B %Y")
portfolio = load_portfolio()


@app.route("/")
def home():
    sgd_balance = "{:.2f}".format(portfolio.sgd_balance)
    usd_balance = "{:.2f}".format(portfolio.usd_balance)
    transactions = portfolio.transaction_history
    fundings = portfolio.funding_history
    holdings = portfolio.holdings
    return render_template("home.html", date=current_date, sgd_balance=sgd_balance, holdings=holdings,
    usd_balance=usd_balance, transactions=transactions, fundings=fundings)


@app.route("/update-balance", methods=["GET", "POST"])
def update_balance():
    if request.method == "POST":
        # Update balance data
        form_data = request.form
        new_sgd_balance = float(form_data.get("sgd_balance"))
        new_usd_balance = float(form_data.get("usd_balance"))
        portfolio.update_balance("SGD", new_sgd_balance)
        portfolio.update_balance("USD", new_usd_balance)
        portfolio.save()
        return redirect(url_for('home'))

    else:
        current_sgd_balance = "{:.2f}".format(portfolio.sgd_balance)
        current_usd_balance = "{:.2f}".format(portfolio.usd_balance)
        return render_template('update-balance.html', sgd_balance=current_sgd_balance,
                                usd_balance=current_usd_balance)


@app.route("/update-funding", methods=["GET", "POST"])
def update_funding():
    if request.method == "POST":
        # Append new funding to funding history
        form_data = request.form
        date = form_data.get("input_date")
        amount = float(form_data.get("amount"))
        portfolio.fund_account(date, amount)
        portfolio.save()
        return redirect(url_for('home'))

    else:
        return render_template("update-funding.html", date=current_date)


@app.route("/update-transaction", methods=["GET", "POST"])
def update_transaction():
    if request.method == "POST":
        # Append new transaction to transaction history
        form_data = request.form
        name = form_data.get("stock_name")
        market_code = form_data.get("stock_code")
        direction = form_data.get("stock_direction")
        price = float(form_data.get("stock_price"))
        currency = form_data.get("stock_currency")
        quantity = int(form_data.get("stock_quantity"))
        if direction == "BUY":
            portfolio.purchase_stock(name, market_code, quantity, price, currency)
        else:
            portfolio.sell_stock(name, market_code, quantity, price, currency)

        portfolio.save()
        return redirect(url_for('home'))

    else:
        return render_template("update-transactions.html")


if __name__ == "__main__":
    app.run(debug=True)