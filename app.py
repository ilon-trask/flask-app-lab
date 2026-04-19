from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def resume():
    return render_template("resume.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


if __name__ == "__name__":
    app.run(debug=True)
