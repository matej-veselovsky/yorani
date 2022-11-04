from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)


def getLastUpdate():
    response = requests.get("https://api.github.com/repos/matej-veselovsky/yorani/commits?path=yorani.db")
    databaseData = json.loads(response.text)
    lastUpdate = databaseData[0]["commit"]["committer"]["date"]
    lastUpdateDate = datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ")

    return lastUpdateDate

def translate(inputWord):
    with sqlite3.connect("yorani.db") as con:
        cur = con.cursor()

        con.create_collation("unicode_nocase",
            lambda x, y : 1 if x.lower() > y.lower() \
                else -1 if x.lower() < y.lower() else 0)


        query = "SELECT czech_word FROM czech_words WHERE reference_id IN (SELECT yorani_id FROM yorani_words WHERE (yorani_word IS ? COLLATE unicode_nocase));"
        cur.execute(query, [inputWord])
        answer = cur.fetchall()

        if answer:
            return answer
        else:
            query = "SELECT yorani_word FROM yorani_words WHERE yorani_id IN (SELECT reference_id FROM czech_words WHERE (czech_word LIKE ? COLLATE unicode_nocase));"
            cur.execute(query, [inputWord + "%"])
            answer = cur.fetchall()

            if answer:
                return answer
            else:
                return 0


def getAllTranslations(inputWord):
    firstOrderList = translate(inputWord)
    if firstOrderList == 0:
        return 0
    
    secondOrderList = []

    for translation in firstOrderList:
        temp = []
        
        for element in translate(translation[0]):
            temp.append(element[0])     
        
        secondOrderList.append([translation[0], temp])
    
    return secondOrderList



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
    date = getLastUpdate().strftime("%-d. %-m. %Y   %H:%M")

    if request.method == "POST":
        inputWord = request.form.get("inputWord").strip()

        tempList = getAllTranslations(inputWord)
        if tempList == 0:
            return render_template("dictionary.html", wordList = 0, displayInput = inputWord, updateDate = date)

        outputList = []

        for row in tempList:
            translation = row[0]
            tempRow = ""
            for element in row[1]:
                tempRow += " "+ element + ","
            tempRow = tempRow.lstrip().rstrip(",")

            outputList.append([translation, tempRow])



        return render_template("dictionary.html", wordList = outputList, displayInput = inputWord, updateDate = date)

    return render_template("dictionary.html", displayInput = False, updateDate = date)

    if __name__ == "__main__":
        app.run()