from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "cupcake_secret"

# ----------------------------------------
# BANCO DE DADOS
# ----------------------------------------

def get_db():
    conn = sqlite3.connect("cupcakes.db")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS cupcakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            image_url TEXT
        )
    """)

    # verifica se já existem registros
    c.execute("SELECT COUNT(*) FROM cupcakes")
    count = c.fetchone()[0]

    if count == 0:
        cupcakes = [
            ("Cupcake Red Velvet", "Cobertura de cream cheese e massa macia.", 12.90,
             "/static/images/redvelvet.jpg"),
            ("Cupcake Chocolate", "Massa de chocolate com ganache cremoso.", 10.50,
             "/static/images/chocolate.jpg"),
            ("Cupcake Baunilha", "Sabor clássico com cobertura suave de baunilha.", 9.90,
             "/static/images/vanilla.jpg"),
            ("Cupcake Morango", "Massa leve com topping natural de morango.", 11.50,
             "/static/images/strawberry.jpg"),
        ]

        c.executemany("""
            INSERT INTO cupcakes (name, description, price, image_url)
            VALUES (?, ?, ?, ?)
        """, cupcakes)

        conn.commit()

    conn.close()

init_db()

# ----------------------------------------
# ROTAS PRINCIPAIS
# ----------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/catalogo")
def catalogo():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM cupcakes")
    cupcakes = c.fetchall()
    conn.close()
    return render_template("catalog.html", cupcakes=cupcakes)

# ----------------------------------------
# CRUD
# ----------------------------------------

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        descricao = request.form["descricao"]
        imagem = request.form.get("imagem", "/static/images/default.jpg")  # opcional

        conn = sqlite3.connect("cupcakes.db")
        c = conn.cursor()

        c.execute("""
            INSERT INTO cupcakes (name, price, description, image_url)
            VALUES (?, ?, ?, ?)
        """, (nome, preco, descricao, imagem))

        conn.commit()
        conn.close()

    @app.route("/delete/<int:id>", methods=["DELETE"])
    def delete(id):
        conn = sqlite3.connect("cupcakes.db")
        c = conn.cursor()
        c.execute("DELETE FROM cupcakes WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for("catalogo"))


        return redirect(url_for("catalogo"))

    return render_template("add.html")

# ----------------------------------------
# CARRINHO
# ----------------------------------------

@app.route("/add_to_cart/<int:id>", methods=["POST"])
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True
    return redirect("/cart")

@app.route("/remove_from_cart/<int:id>", methods=["POST"])
def remove_from_cart(id):
    if "cart" in session:
        if id in session["cart"]:
            session["cart"].remove(id)
            session.modified = True
    return redirect("/cart")

@app.route("/cart")
def cart():
    if "cart" not in session:
        session["cart"] = []

    conn = get_db()
    c = conn.cursor()

    itens = []
    total = 0

    for cupcake_id in session["cart"]:
        c.execute("SELECT * FROM cupcakes WHERE id=?", (cupcake_id,))
        item = c.fetchone()
        if item:
            itens.append(item)
            total += item[3]  # índice certo do preço

    conn.close()
    return render_template("cart.html", itens=itens, total=total)

@app.route("/checkout")
def checkout():
    session["cart"] = []
    return render_template("checkout.html")

if __name__ == "__main__":
    app.run(debug=False)
