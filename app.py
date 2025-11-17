from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "cupcake_secret"

# -----------------------
# BANCO DE DADOS
# -----------------------

def init_db():
    if not os.path.exists("cupcakes.db"):
        conn = sqlite3.connect("cupcakes.db")
        c = conn.cursor()
        c.execute("""
        CREATE TABLE cupcakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            descricao TEXT
        )
        """)
        conn.commit()
        conn.close()

init_db()

# -----------------------
# ROTAS PRINCIPAIS
# -----------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/catalogo")
def catalogo():
    conn = sqlite3.connect("cupcakes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cupcakes")
    cupcakes = c.fetchall()
    conn.close()
    return render_template("catalog.html", cupcakes=cupcakes)

# -----------------------
# CRUD CUPCAKES
# -----------------------

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = request.form["preco"]
        descricao = request.form["descricao"]

        conn = sqlite3.connect("cupcakes.db")
        c = conn.cursor()
        c.execute("INSERT INTO cupcakes (nome, preco, descricao) VALUES (?, ?, ?)",
                  (nome, preco, descricao))
        conn.commit()
        conn.close()

        return redirect(url_for("catalogo"))

    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("cupcakes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cupcakes WHERE id = ?", (id,))
    cupcake = c.fetchone()

    if request.method == "POST":
        nome = request.form["nome"]
        preco = request.form["preco"]
        descricao = request.form["descricao"]

        c.execute("UPDATE cupcakes SET nome=?, preco=?, descricao=? WHERE id=?",
                  (nome, preco, descricao, id))
        conn.commit()
        conn.close()
        return redirect(url_for("catalogo"))

    conn.close()
    return render_template("edit.html", cupcake=cupcake)

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("cupcakes.db")
    c = conn.cursor()
    c.execute("DELETE FROM cupcakes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("catalogo"))

# -----------------------
# CARRINHO
# -----------------------

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(id)
    return redirect(url_for("catalogo"))

@app.route("/cart")
def cart():
    if "cart" not in session:
        session["cart"] = []

    conn = sqlite3.connect("cupcakes.db")
    c = conn.cursor()

    itens = []
    total = 0

    for cupcake_id in session["cart"]:
        c.execute("SELECT * FROM cupcakes WHERE id=?", (cupcake_id,))
        item = c.fetchone()
        if item:
            itens.append(item)
            total += item[2]

    conn.close()
    return render_template("cart.html", itens=itens, total=total)

@app.route("/checkout")
def checkout():
    session["cart"] = []
    return render_template("checkout.html")

if __name__ == "__main__":
    app.run(debug=True)
