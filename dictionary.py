from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

def translate(inputWord):
    with sqlite3.connect("yorani.db") as con:
        cur = con.cursor()

        inputWordLower = inputWord.lower()
        inputWordUpper = inputWord.upper()

        query = "SELECT czech_word FROM czech_words WHERE reference_id IN (SELECT yorani_id FROM yorani_words WHERE (yorani_word IS ? COLLATE NOCASE) OR (yorani_word IS ? COLLATE NOCASE));"
        cur.execute(query, (inputWordLower, inputWordUpper))
        answer = cur.fetchall()

        if answer:
            return answer
        else:
            query = "SELECT yorani_word FROM yorani_words WHERE yorani_id IN (SELECT reference_id FROM czech_words WHERE (czech_word IS ? COLLATE NOCASE) OR (czech_word IS ? COLLATE NOCASE));"
            cur.execute(query, (inputWordLower, inputWordUpper))
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

    if request.method == "POST":
        inputWord = request.form.get("inputWord").strip()

        tempList = getAllTranslations(inputWord)
        if tempList == 0:
            return render_template("dictionary.html", wordList = 0, displayInput = inputWord)

        outputList = []

        for row in tempList:
            translation = row[0]
            tempRow = ""
            for element in row[1]:
                tempRow += " "+ element + ","
            tempRow = tempRow.lstrip().rstrip(",")

            outputList.append([translation, tempRow])



        return render_template("dictionary.html", wordList = outputList, displayInput = inputWord)

    return render_template("dictionary.html", displayInput = False)

    if __name__ == "__main__":
        app.run()