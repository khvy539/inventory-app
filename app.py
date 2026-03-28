from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db():
    return sqlite3.connect("inventory.db")

# 初期化
def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        stock REAL,
        threshold REAL,
        unit TEXT
    )
    """)
    db.commit()
    db.close()

@app.route("/")
def index():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    db.close()
    return render_template("index.html", products=products)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO products (name, category, stock, threshold, unit) VALUES (?, ?, ?, ?, ?)",
            (request.form["name"], request.form["category"],
             request.form["stock"], request.form["threshold"], request.form["unit"])
        )
        db.commit()
        db.close()
        return redirect("/")
    return render_template("add.html")

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    db = get_db()

    if request.method == "POST":
        qty = float(request.form["quantity"])
        action = request.form["action"]

        # 🔥 同時編集を考慮した安全更新
        if action == "in":
            db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, id))
        else:
            db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, id))

        db.commit()
        db.close()
        return redirect("/")

    product = db.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    db.close()
    return render_template("update.html", product=product)

@app.route("/alert")
def alert():
    db = get_db()
    products = db.execute("SELECT * FROM products WHERE stock <= threshold").fetchall()
    db.close()
    return render_template("index.html", products=products)

import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
