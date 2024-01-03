from flask import Flask , render_template, request, redirect
from cs50 import SQL
import random

app = Flask(__name__)
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
        if choice == "4":
            return redirect("/showresults")
        else:
            return render_template("index.html")
    return render_template("index.html")

@app.route("/showresults", methods=["GET", "POST"])
def showresults():
    if request.method == "POST":
        id = request.form.get("choice")
        if not id:
            return render_template('failure.html')
        id = int(id)
        test = db.execute("SELECT * FROM tests WHERE id = ?", id)
        date = db.execute("SELECT day, month FROM results WHERE id = ?", id)[0]
        day = int(date['day'])
        month = int(date['month'])
        return render_template('showresult.html', test = test, day = day, month = month)

    days = db.execute("SELECT DISTINCT(day) FROM vocab")
    months = db.execute("SELECT DISTINCT(month) FROM vocab")
    days = [days[i]['day'] for i in range(len(days))]
    months = [months[i]['month'] for i in range(len(months))]
    # add all day and month to create a temp date
    temp = []
    for i in range(len(days)):
        for j in range(len(months)):
            temp.append([days[i], months[j]])
    # only choose date where there is data
    dates = []
    for day, month in temp:
        if (len(db.execute("SELECT * FROM vocab WHERE day = ? AND month = ?", day, month)) != 0):
            dates.append([day, month])
    results = []
    for day, month in dates:
        results += db.execute("SELECT * FROM results WHERE day = ? AND month = ?", day, month)
    return render_template("takedate.html", results = results)

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
        for i in range(len(vocabs)):
            vocabs[i].update({'num': i + 1})
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
        global current_month
        global current_day
        correct = 0
        for i in range(len(vocabs_main)):
            viet = vocabs_main[i]['viet']
            answer = request.form.get(viet)
            eng = vocabs_main[i]['eng']
            num = vocabs_main[i]['num']
            if answer == eng:
                correct += 1
            answers.append({'answer': answer, 'eng': eng, 'viet': viet, 'num': num})
        corrects = db.execute("SELECT correct FROM results WHERE day = ? AND month = ?", current_day, current_month)
        # Find the id
        id = 0
        if len(corrects) == 0:
            id = db.execute("SELECT MAX(id) AS id FROM results")[0]['id']
            if not id:
                id = 1
            else:
                id += 1
            db.execute("INSERT INTO results (id, day, month, correct, total, score) VALUES (?, ?, ?, ?, ?, ?)", 
                id, current_day, current_month, correct, len(vocabs_main), round(10 * correct / len(vocabs_main), 2))
            for answer in answers:
                db.execute("INSERT INTO tests (id, day, month, eng, viet, answer) VALUES (?, ?, ?, ?, ?, ?)",
                    id, current_day, current_month, answer['eng'], answer['viet'], answer['answer'])
        else:
            id = db.execute("SELECT id FROM results WHERE day = ? AND month = ?", current_day, current_month)[0]['id']
            
            last_test = db.execute("SELECT eng, answer FROM tests WHERE id = ?", id)
            
            for answer in answers:
                for row in last_test:
                    if answer['eng'] == row['eng']:
                        answer.update({'last_answer': row['answer']})
            last_correct = db.execute("SELECT correct FROM results WHERE id = ?", id)[0]['correct']
            if correct > corrects[0]['correct']:
                # give user an announcement whether they get better or worse
                announcement = "Congratulations! You did much better than your last test."
                # delete last result and test
                db.execute("DELETE FROM results WHERE id = ?", id)
                db.execute("DELETE FROM tests WHERE id = ?", id)
                # add the recent result and test
                db.execute("INSERT INTO results (id, day, month, correct, total, score) VALUES (?, ?, ?, ?, ?, ?)", 
                    id, current_day, current_month, correct, len(vocabs_main), round(10 * correct / len(vocabs_main), 2))
                for answer in answers:
                    db.execute("INSERT INTO tests (id, day, month, eng, viet, answer) VALUES (?, ?, ?, ?, ?, ?)",
                        id, current_day, current_month, answer['eng'], answer['viet'], answer['answer'])
            elif correct < corrects[0]['correct']:
                announcement = "Seems like you did not prepare good enough. Take test again!"
            else:
                announcement = "So far so good. You got same result as your last test"
        # if user has not done any test, then just give them feedback of their current test
        if len(corrects) == 0:
            return render_template('results.html', answers = answers, correct = correct, total = len(vocabs_main))
        # else give the user feedback of the current and the last one
        else:
            return render_template('results_with_comparison.html', 
                                   answers = answers, correct = correct, total = len(vocabs_main), announcement = announcement, last_correct = last_correct)
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
        temp_dates = []
        for day, month in temp:
            if (len(db.execute("SELECT * FROM vocab WHERE day = ? AND month = ?", day, month)) != 0):
                temp_dates.append([day, month])
        dates = []
        for date in temp_dates:
            score = db.execute("SELECT score FROM results WHERE day = ? AND month = ?",
                                 date[0], date[1])
            if len(score) > 0 and score[0]['score'] >= 9:
                dates.append(date)
        return render_template("show.html", dates=dates)
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
        vocabs_add.insert(0, {'viet':viet, 'eng':eng})
        return render_template("add.html", vocabs = vocabs_add, day = current_day, month = current_month)  
    vocabs_add = []
    return render_template("add.html", vocabs = vocabs_add, day = current_day, month = current_month)

@app.route("/addfirst", methods=["GET", "POST"])
def addfirst():
    global vocabs_add
    global current_day
    global current_month
    if len(vocabs_add) != 0:
        return render_template("add.html", vocabs = vocabs_add, day = current_day, month = current_month)
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
                    break
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


