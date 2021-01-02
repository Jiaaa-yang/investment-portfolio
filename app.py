from flask import Flask, url_for, render_template, request, redirect
from update_data import read_data, write_data
from datetime import datetime


# Key shortcuts for accessing data
SGD_KEY = "sgd_balance"
USD_KEY = "usd_balance"


app = Flask(__name__)
data_file = 'data.json'
current_date = datetime.now().strftime("%d %B %Y")


@app.route("/")
def home():
    sgd_balance = read_data(data_file, SGD_KEY)
    usd_balance = read_data(data_file, USD_KEY)
    transactions = read_data(data_file, "transactions")
    fundings = read_data(data_file, "fundings")
    return render_template("home.html", date=current_date, sgd_balance=sgd_balance,
    usd_balance=usd_balance, transactions=transactions, fundings=fundings)


@app.route("/update-balance", methods=["GET", "POST"])
def update_balance():
    if request.method == "POST":
        # Update balance data
        form_data = request.form
        new_sgd_balance = form_data.get(SGD_KEY)
        new_usd_balance = form_data.get(USD_KEY)
        write_data(data_file, SGD_KEY, new_sgd_balance)
        write_data(data_file, USD_KEY, new_usd_balance)
        return redirect(url_for('home'))

    else:
        current_sgd_balance = read_data(data_file, SGD_KEY)
        current_usd_balance = read_data(data_file, USD_KEY)
        return render_template('update-balance.html', sgd_balance=current_sgd_balance,
                                usd_balance=current_usd_balance)


@app.route("/update-funding", methods=["GET", "POST"])
def update_funding():
    if request.method == "POST":
        # Append new funding to funding history
        form_data = request.form
        new_funding = {
            "date": form_data.get("input_date"),
            "amount": form_data.get("amount")
        }
        write_data(data_file, "fundings", new_funding)
        return redirect(url_for('home'))

    else:
        return render_template("update-funding.html", date=current_date)


@app.route("/update-transaction", methods=["GET", "POST"])
def update_transaction():
    if request.method == "POST":
        # Append new transaction to transaction history
        form_data = request.form
        new_transaction = {
            "name": form_data.get("stock_name"),
            "direction": form_data.get("stock_direction"),
            "price": form_data.get("stock_price"),
            "currency": form_data.get("stock_currency"),
            "quantity": form_data.get("stock_quantity")
        }
        write_data(data_file, "transactions", new_transaction)
        return redirect(url_for('home'))

    else:
        return render_template("update-transactions.html")


if __name__ == "__main__":
    app.run(debug=True)
