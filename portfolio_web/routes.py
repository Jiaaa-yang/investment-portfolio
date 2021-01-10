from flask import render_template, url_for, redirect, request
from datetime import datetime
from portfolio_web import app
from portfolio_web.portfolio_update import *


current_date = datetime.now().strftime("%d %B %Y")


@app.route("/")
def home():
    profits = get_main_data("profits")
    commissions = get_main_data("commissions") 
    cash_balance = get_main_data("cash_balance")
    profits_sgd = "{:.2f}".format(profits["sgd"])
    profits_usd = "{:.2f}".format(profits["usd"])
    commissions_sgd = "{:.2f}".format(commissions["sgd"])
    commissions_usd = "{:.2f}".format(commissions["usd"])
    cash_sgd = "{:.2f}".format(cash_balance["sgd"])
    cash_usd = "{:.2f}".format(cash_balance["usd"])
    holdings = get_main_data("holdings")
    transactions = get_transaction_history()
    balances = get_balance_history()
    return render_template("home.html", date=current_date, holdings=holdings,
    transactions=transactions, balances=balances, profits_sgd=profits_sgd,
    profits_usd=profits_usd, commissions_sgd=commissions_sgd, commissions_usd=commissions_usd,
    cash_sgd=cash_sgd, cash_usd=cash_usd)


@app.route("/update-balance", methods=["GET", "POST"])
def update_balance():
    if request.method == "POST":
        # Update balance data
        form_data = request.form
        new_cash_sgd = float(form_data.get("cash_sgd"))
        new_cash_usd = float(form_data.get("cash_usd"))
        update_main_data("cash_balance", new_cash_sgd, new_cash_usd)
        return redirect(url_for('home'))

    else:
        cash_balance = get_main_data("cash_balance")
        cash_sgd = "{:.2f}".format(cash_balance["sgd"])
        cash_usd = "{:.2f}".format(cash_balance["usd"])
        return render_template('update-balance.html', cash_sgd=cash_sgd, cash_usd=cash_usd)


@app.route("/update-funding", methods=["GET", "POST"])
def update_funding():
    if request.method == "POST":
        form_data = request.form
        funding_type = form_data.get("type")
        # Update new funding
        if funding_type == "funding":
            date = form_data.get("funding_date")
            amount = float(form_data.get("amount"))
            fund_account(date, amount)

        # Update new currency exchange
        elif funding_type == "currency_exchange":
            date = form_data.get("exchange_date")
            direction = form_data.get("direction") 
            sgd = float(form_data.get("sgd"))
            usd = float(form_data.get("usd"))
            exchange_currency(date, direction, sgd, usd)
            
        else:
            raise Exception("Unknown funding type")

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