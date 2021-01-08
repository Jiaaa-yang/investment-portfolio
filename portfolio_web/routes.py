from flask import render_template, url_for, redirect, request
from datetime import datetime
from portfolio_web import app
from portfolio_web.portfolio_update import *


current_date = datetime.now().strftime("%d %B %Y")


@app.route("/")
def home():
    portfolio = read_portfolio()
    sgd_balance = "{:.2f}".format(portfolio["sgd_balance"])
    usd_balance = "{:.2f}".format(portfolio["usd_balance"])
    holdings = portfolio["holdings"]
    transactions = get_history("transaction") 
    fundings = get_history("funding")
    return render_template("home.html", date=current_date, sgd_balance=sgd_balance, holdings=holdings,
    usd_balance=usd_balance, transactions=transactions, fundings=fundings)


@app.route("/update-balance", methods=["GET", "POST"])
def update_balance():
    if request.method == "POST":
        # Update balance data
        form_data = request.form
        new_sgd_balance = float(form_data.get("sgd_balance"))
        new_usd_balance = float(form_data.get("usd_balance"))
        update_account_balance(new_sgd_balance, new_usd_balance)
        return redirect(url_for('home'))

    else:
        portfolio = read_portfolio()
        current_sgd_balance = "{:.2f}".format(portfolio["sgd_balance"])
        current_usd_balance = "{:.2f}".format(portfolio["usd_balance"])
        return render_template('update-balance.html', sgd_balance=current_sgd_balance,
                                usd_balance=current_usd_balance)


@app.route("/update-funding", methods=["GET", "POST"])
def update_funding():
    if request.method == "POST":
        # Append new funding to funding history
        form_data = request.form
        date = form_data.get("input_date")
        amount = float(form_data.get("amount"))
        fund_account(date, amount)
        return redirect(url_for('home'))

    else:
        return render_template("update-funding.html", date=current_date)


@app.route("/update-transaction", methods=["GET", "POST"])
def update_transaction():
    if request.method == "POST":
        # Append new transaction to transaction history
        form_data = request.form
        name = form_data.get("name")
        market_code = form_data.get("market_code")
        price = float(form_data.get("price"))
        quantity = int(form_data.get("quantity"))
        currency = form_data.get("currency")
        direction = form_data.get("inlineRadioOptions")

        if direction == "BUY":
            purchase_stock(name, market_code, quantity, price, currency)
        else:
            sell_stock(name, market_code, quantity, price, currency)

        return redirect(url_for('home'))

    else:
        return render_template("update-transactions.html")