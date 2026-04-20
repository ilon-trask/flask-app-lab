from flask import render_template, request, url_for, redirect
from . import products


@products.route("/product/<string:name>")
def product(name):
    name = name.upper()
    price = request.args.get("price", None, int)

    return render_template("product.html", name=name, price=price)


@products.route("/theproduct")
def theproduct():
    to_url = url_for("products.product", name="makbook", price=900, _external=True)
    print("to_url", to_url)
    return redirect(to_url)
