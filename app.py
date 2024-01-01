from flask import Flask , render_template, request, redirect
from cs50 import SQL
import random

app=Flask(__name__)
db = SQL("sqlite:///vocab.db")

vocabs_main = []
vocabs_add = []
current_day = 0
current_month = 0

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        choice = request.form.get("choice");
        if not choice:
            return render_template("failure.html")
        if choice == "1":
            return redirect("/testchoice")
        if choice == "2":
            return redirect("/addfirst")
        if choice == "3":
            return redirect("/show")
    return render_template("index.html")

@app.route("/testchoice", methods=["GET", "POST"])
def testchoice():
    if request.method == "GET":
        day = db.execute("SELECT DISTINCT(day) FROM vocab")
        month = db.execute("SELECT DISTINCT(month) FROM vocab")
        day = [day[i]['day'] for i in range(len(day))]
        month = [month[i]['month'] for i in range(len(month))]
        # add all day and month to create a temp date
        temp = []
        for i in range(len(day)):
            for j in range(len(month)):
                temp.append([day[i], month[j]])
        # only choose date where there is data
        date = []
        for day, month in temp:
            if (len(db.execute("SELECT * FROM vocab WHERE day = ? AND month = ?", day, month)) != 0):
                date.append([day, month])
        return render_template("testchoice.html", dates=date)
    else:
        choice = request.form.get("choice")
        if not choice:
            return render_template('failure.html')
        choice = choice.split('/')
        day, month = int(choice[0]), int(choice[1])
        vocabs = db.execute('SELECT viet, eng FROM vocab WHERE day = ? AND month = ?', day, month)
        random.shuffle(vocabs)
        global vocabs_main
        global current_month
        global current_day
        current_day = day
        current_month = month
        vocabs_main = vocabs
        return render_template('test.html', vocabs = vocabs)
    
@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        answers = []
        global vocabs_main
        count = 0
        for i in range(len(vocabs_main)):
            viet = vocabs_main[i]['viet']
            answer = request.form.get(viet)
            result = vocabs_main[i]['eng']
            if answer == result:
                count += 1
            answers.append({'answer': answer, 'result': result, 'viet': viet})
        
        return render_template('results.html', answers = answers, correct = count, total = len(vocabs_main))
    return redirect("/")

@app.route("/show", methods=["GET", "POST"])
def show():
    if request.method == "GET":
        # shows user all dates possible
        day = db.execute("SELECT DISTINCT(day) FROM vocab")
        month = db.execute("SELECT DISTINCT(month) FROM vocab")
        day = [day[i]['day'] for i in range(len(day))]
        month = [month[i]['month'] for i in range(len(month))]
        # add all day and month to create a temp date
        temp = []
        for i in range(len(day)):
            for j in range(len(month)):
                temp.append([day[i], month[j]])
        # only choose date where there is data
        date = []
        for day, month in temp:
            if (len(db.execute("SELECT * FROM vocab WHERE day = ? AND month = ?", day, month)) != 0):
                date.append([day, month])
        return render_template("show.html", dates=date)
    else:
        # shows contents of the dates given by user
        choice = request.form.get("choice")
        if not choice:
            return render_template('failure.html')
        choice = choice.split('/')
        day, month = int(choice[0]), int(choice[1])
        vocabs = db.execute('SELECT viet, eng FROM vocab WHERE day = ? AND month = ?', day, month)
        global vocabs_main
        global current_day
        global current_month
        current_day = day
        current_month = month
        vocabs_main = vocabs
        for i in range(len(vocabs_main)):
            vocabs_main[i].update({'num': i + 1})
        return render_template('delete.html', vocabs = vocabs, day = day, month = month)
    
@app.route("/deletedata", methods=["POST", "GET"])
def deletedata():
    # delete all datas from the date
    if request.method == "POST":
        db.execute("DELETE FROM vocab WHERE day = ? AND month = ?", current_day, current_month)
    return redirect("/")
    
@app.route("/add", methods=["GET", "POST"])
def add():
    global vocabs_add
    global current_day
    global current_month
    if request.method == "POST":
        if current_day == 0:
            day = int(request.form.get('day'))
            month = int(request.form.get('month'))
            current_day = day
            current_month = month
        viet = request.form.get('viet')
        eng = request.form.get('eng')
        vocabs_add.append({'viet':viet, 'eng':eng})
        return render_template("add.html", vocabs = vocabs_add, day = current_day, month = current_month)  
    vocabs_add = []
    return render_template("add.html", vocabs = vocabs_add, day = current_day, month = current_month)

@app.route("/addfirst", methods=["GET", "POST"])
def addfirst():
    global vocabs_add
    global current_day
    global current_month
    current_day = 0
    current_month = 0
    vocabs_add == []
    return render_template("addfirst.html")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    global vocabs_add
    global current_day
    global current_month
    if request.method == "POST":
        delete = request.form.get("delete")    
        if delete:
            for i in range(len(vocabs_add)):
                if vocabs_add[i]['eng'] == delete:
                    del vocabs_add[i]
        return render_template("add.html", vocabs = vocabs_add, day = current_day, month=current_month)
    return redirect("/")

@app.route("/finish", methods=["GET", "POST"])
def finish():
    global vocabs_add
    global current_day
    global current_month
    if request.method == "POST":
        viet = request.form.get('viet')
        eng = request.form.get('eng')
        if viet and eng:
            if vocabs_add[-1]['eng'] != eng:
                vocabs_add.append({'viet':viet, 'eng':eng})
        for i in range(len(vocabs_add)):
            db.execute("INSERT INTO vocab(day, month, viet, eng) VALUES(?, ?, ?, ?)", current_day, current_month, vocabs_add[i]['viet'], vocabs_add[i]['eng'])
    vocabs_add = []
    current_day = 0
    current_month = 0
    return redirect("/")


