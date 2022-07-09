from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

def translate(inputWord, direction):
    with sqlite3.connect("yorani.db") as con:
        cur = con.cursor()

        if direction == "ytoc":
            query = "SELECT czech_word FROM czech_words WHERE reference_id IN (SELECT yorani_id FROM yorani_words WHERE yorani_word IS (?) COLLATE NOCASE);"
        else:
            query = "SELECT yorani_word FROM yorani_words WHERE yorani_id IN (SELECT reference_id FROM czech_words WHERE czech_word IS (?) COLLATE NOCASE);"

        cur.execute(query, [inputWord])
        answer = cur.fetchall()

        if answer:
            return answer
        else:
            return 0



@app.route("/")
def index():
    return render_template("index.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/png')


@app.route("/dictionary", methods=["GET", "POST"])
def dictionary():
    outputList = ""

    if request.method == "POST":
        inputWord = request.form.get("inputWord")
        direction = request.form.get("direction")

        outputList = translate(inputWord, direction)
        return render_template("dictionary.html", wordList = outputList)

    return render_template("dictionary.html")

    if __name__ == "__main__":
        app.run()