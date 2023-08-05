from datetime import date
import calendar
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tracker.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    global month3
    if request.method == "POST":
        
        today = date.today()
        today = str(today)
        search = today[:-4]

        MONTH = request.form.get('month')
        if MONTH != None:
            MONTH = str(MONTH)
            MONTH = MONTH[-2:]
            if MONTH[:1] == '0':
                month3 = int(MONTH[-1:])
            else:
                month3 = int(MONTH)

        Previous = request.form.get('Previous')
        if Previous != None:
            month3 = int(month3) - 1
        
        Next = request.form.get('Next')
        if Next != None:
            month3 = int(month3) + 1


        if int(month3) > 12 or int(month3) < 1: #check if it overflow
            month3 = today[-4:-3]

        
            
      
        Month_full_name = calendar.month_name[int(month3)]
        search = search + str(month3)
        search = search + '%'

        
        Meta_Category = [' Birthday Gift', 'Business Expense', 'Charity', 'Entertainment','Food','Materialistic Desires','Medical','Rent','Self-Improvement','Transportation','Travel','Other']
        record = {}
        LIST = []
        total = 0 
        for i in Meta_Category:
            record['Meta Category'] = i
            SUM = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ? AND MetaC = ?", session["user_id"],search,i)
            SUM = SUM[0]['SUM(expenses)']
            if SUM == None:
                SUM = 0
            total += SUM
            record['Sum'] = SUM
            record['Percentage'] = 0
            LIST.append(record.copy())
        for i in LIST:
            if i['Sum'] != 0:
                percentage = (i['Sum']/total) * 100
                i['Percentage'] = round(percentage,1)
        return render_template('index.html',LIST=LIST,Month_full_name=Month_full_name, total = total)
    else:
        
        today = date.today()
        today = str(today)
        search = today[:-4]
        month3 = today[-4:-3]

        
        Month_full_name = calendar.month_name[int(month3)]
        search = search + str(month3)
        search = search + '%'


        Meta_Category = [' Birthday Gift', 'Business Expense', 'Charity', 'Entertainment','Food','Materialistic Desires','Medical','Rent','Self-Improvement','Transportation','Travel','Other']
        record = {}
        LIST = []
        total = 0 
        for i in Meta_Category:
            record['Meta Category'] = i
            SUM = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ? AND MetaC = ?", session["user_id"],search,i)
            SUM = SUM[0]['SUM(expenses)']
            if SUM == None:
                SUM = 0
            total += SUM
            record['Sum'] = SUM
            record['Percentage'] = 0
            LIST.append(record.copy())
        for i in LIST:
            if i['Sum'] != 0:
                percentage = (i['Sum']/total) * 100
                i['Percentage'] = round(percentage,1)
        return render_template('index.html',LIST=LIST,Month_full_name=Month_full_name, total = total)
   





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        flag = 'F'
        # Ensure password == confirmation
        if not (password == confirmation):
            return apology("the passwords do not match", 400)

        # Ensure password not blank
        if password == "" or confirmation == "" or username == "":
            return apology("input is blank", 400)

        # Ensure username does not exists already
        if len(rows) == 1:
            return apology("username already exist", 400)
        else:
            hashcode = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashcode)
            flag = 'T'

        if flag == 'T':
            rows1 = db.execute("SELECT * FROM users WHERE username = ?", username)
            session["user_id"] = rows1[0]["id"]
            return redirect("/")
        else:
            # Redirect user to home page
            return redirect("/")
    else:
        return render_template("register.html")


    

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    
    global month
    if request.method == "POST":
        Date = request.form.get('Date')
        Description = request.form.get('Description')
        expenses = request.form.get('expenses')
        Category = request.form.get('Category')
        MetaC = request.form.get('MetaC') #TODO get the month that the search engine search for and return results
        
        if Date:
            db.execute("INSERT INTO Expenses (id, Date,Description,expenses,Category,MetaC) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], Date,Description,expenses,Category,MetaC)
        Delete = request.form.get('Delete')
        if Delete != None:
            db.execute("DELETE FROM Expenses WHERE E_id = ? AND id = ?",Delete,session["user_id"])

        today = date.today()
        today = str(today)
        search = today[:-4]

        MONTH = request.form.get('month')
        if MONTH != None:
            MONTH = str(MONTH)
            MONTH = MONTH[-2:]
            if MONTH[:1] == '0':
                month = int(MONTH[-1:])
            else:
                month = int(MONTH)
        
        
        Previous = request.form.get('Previous')
        if Previous != None:
            month = int(month) -1
        
        Next = request.form.get('Next')
        if Next != None:
            month = int(month) +1


        if int(month) > 12 or int(month) < 1: #check if it overflow
            month = today[-4:-3]

        
            
        Month_full_name = calendar.month_name[int(month)]
        month = str(month)
        search = search + month
        search = search + '%'
        total = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        total = total[0]['SUM(expenses)']
        if total == None:
            total = 0
        
        LIST = db.execute("SELECT * FROM Expenses WHERE id = ? AND Date LIKE ? ORDER BY Date DESC", session["user_id"],search) #TODO Search the data from This month date
        Cat = [' Birthday Gift', 'Business Expense', 'Charity', 'Entertainment','Food','Materialistic Desires','Medical','Other','Rent','Self-Improvement','Transportation','Travel']
        return render_template('expenses.html',Cat=Cat,LIST=LIST,Month_full_name=Month_full_name, total = total)
    else:
        
        today = date.today()
        today = str(today)
        search = today[:-4]
        month = today[-4:-3]

        
        Month_full_name = calendar.month_name[int(month)]
        search = search + month
        search = search + '%'
        
        total = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        total = total[0]['SUM(expenses)']
        if total == None:
            total = 0
        LIST = db.execute("SELECT * FROM Expenses WHERE id = ? AND Date LIKE ? ORDER BY Date DESC", session["user_id"],search) #TODO Search the data from This month date
        Cat = [' Birthday Gift', 'Business Expense', 'Charity', 'Entertainment','Food','Materialistic Desires','Medical','Other','Rent','Self-Improvement','Transportation','Travel']
        return render_template('expenses.html',Cat=Cat,LIST=LIST,Month_full_name=Month_full_name, total = total)

@app.route("/income", methods=["GET", "POST"])
@login_required
def income():  
    global month1
    if request.method == "POST":
        Date = request.form.get('Date')
        Description = request.form.get('Description')
        income = request.form.get('income')
        Category = request.form.get('Category')
        
        if Date:
            db.execute("INSERT INTO Income (id, Date,Description,income,Category) VALUES(?, ?, ?, ?, ?)", session["user_id"], Date,Description,income,Category)
        Delete = request.form.get('Delete')
        if Delete != None:
            db.execute("DELETE FROM Income WHERE I_id = ? AND id = ?",Delete,session["user_id"])

        today = date.today()
        today = str(today)
        search = today[:-4]

        MONTH = request.form.get('month')
        if MONTH != None:
            MONTH = str(MONTH)
            MONTH = MONTH[-2:]
            if MONTH[:1] == '0':
                month1 = int(MONTH[-1:])
            else:
                month1 = int(MONTH)
        
        
        Previous = request.form.get('Previous')
        if Previous != None:
            month1 = int(month1) -1
        
        Next = request.form.get('Next')
        if Next != None:
            month1 = int(month1) +1


        if int(month1) > 12 or int(month1) < 1: #check if it overflow
            month1 = today[-4:-3]

        
            
        Month_full_name = calendar.month_name[int(month1)]
        month1 = str(month1)
        search = search + month1
        search = search + '%'
        total = db.execute("SELECT SUM(income) FROM Income WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        total = total[0]['SUM(income)']
        if total == None:
            total = 0
        
        LIST = db.execute("SELECT * FROM Income WHERE id = ? AND Date LIKE ? ORDER BY Date DESC", session["user_id"],search) #TODO Search the data from This month date
        
        return render_template('income.html',LIST=LIST,Month_full_name=Month_full_name, total = total)
    else:
        
        today = date.today()
        today = str(today)
        search = today[:-4]
        month1 = today[-4:-3]

        
        Month_full_name = calendar.month_name[int(month1)]
        search = search + month1
        search = search + '%'
        
        total = db.execute("SELECT SUM(income) FROM Income WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        total = total[0]['SUM(income)']
        
        if total == None:
            total = 0
        LIST = db.execute("SELECT * FROM Income WHERE id = ? AND Date LIKE ? ORDER BY Date DESC", session["user_id"],search) #TODO Search the data from This month date
       
        return render_template('income.html',LIST=LIST,Month_full_name=Month_full_name, total = total)


@app.route("/netincome", methods=["GET", "POST"])
@login_required
def netincome():
    global month2
    if request.method == "POST":
        
        today = date.today()
        today = str(today)
        search = today[:-4]

        MONTH = request.form.get('month')
        if MONTH != None:
            MONTH = str(MONTH)
            MONTH = MONTH[-2:]
            if MONTH[:1] == '0':
                month2 = int(MONTH[-1:])
            else:
                month2 = int(MONTH)

        Previous = request.form.get('Previous')
        if Previous != None:
            month2 = int(month2) -1
        
        Next = request.form.get('Next')
        if Next != None:
            month2 = int(month2) +1


        if int(month2) > 12 or int(month2) < 1: #check if it overflow
            month2 = today[-4:-3]

        
            
      
        Month_full_name = calendar.month_name[int(month2)]
        search = search + str(month2)
        search = search + '%'
        
        Income = db.execute("SELECT SUM(income) FROM Income WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        Income = Income[0]['SUM(income)']
        if Income == None:
            Income = 0
        Expenses = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        Expenses = Expenses[0]['SUM(expenses)']
        if Expenses == None:
            Expenses = 0
        total = int(Income) - int(Expenses)
        
        return render_template('netincome.html',Month_full_name=Month_full_name, Income = Income, Expenses=Expenses, total = total)
    else:
        
        today = date.today()
        today = str(today)
        search = today[:-4]
        month2 = today[-4:-3]

        
        Month_full_name = calendar.month_name[int(month2)]
        search = search + str(month2)
        search = search + '%'
        
        Income = db.execute("SELECT SUM(income) FROM Income WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        Income = Income[0]['SUM(income)']
        if Income == None:
            Income = 0
        Expenses = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        Expenses = Expenses[0]['SUM(expenses)']
        if Expenses == None:
            Expenses = 0
        total = int(Income) - int(Expenses)
        
        return render_template('netincome.html',Month_full_name=Month_full_name, Income = Income, Expenses=Expenses, total = total)


@app.route("/asset", methods=["GET", "POST"])
@login_required
def asset():
    if request.method == "POST":
        Description = request.form.get('Description')
        value = request.form.get('value')
        Category = request.form.get('Category')
        
        if Description:
            db.execute("INSERT INTO Asset (id, Description,Value,Category) VALUES(?, ?, ?, ?)", session["user_id"], Description,value,Category)
        Delete = request.form.get('Delete')
        if Delete != None:
            db.execute("DELETE FROM Asset WHERE A_id = ? AND id = ?",Delete,session["user_id"])

       
        total = db.execute("SELECT SUM(Value) FROM Asset WHERE id = ?", session["user_id"])
        total = total[0]['SUM(Value)']
        if total == None:
            total = 0
        
        LIST = db.execute("SELECT * FROM Asset WHERE id = ? ORDER BY Value DESC", session["user_id"])         
        return render_template('asset.html',LIST=LIST,total = total)
    else:
        total = db.execute("SELECT SUM(Value) FROM Asset WHERE id = ?", session["user_id"])
        total = total[0]['SUM(Value)']
        if total == None:
            total = 0
        
        LIST = db.execute("SELECT * FROM Asset WHERE id = ? ORDER BY Value DESC", session["user_id"])         
        return render_template('asset.html',LIST=LIST,total = total)


@app.route("/liabilities", methods=["GET", "POST"])
@login_required
def liabilities():
    if request.method == "POST":
        Description = request.form.get('Description')
        owed = request.form.get('owed')
        Category = request.form.get('Category')
        
        if Description:
            db.execute("INSERT INTO Liabilities (id, Description,Owed,Category) VALUES(?, ?, ?, ?)", session["user_id"], Description,owed,Category)
        Delete = request.form.get('Delete')
        if Delete != None:
            db.execute("DELETE FROM Liabilities WHERE L_id = ? AND id = ?",Delete,session["user_id"])

       
        total = db.execute("SELECT SUM(Owed) FROM Liabilities WHERE id = ?", session["user_id"])
        total = total[0]['SUM(Owed)']
        if total == None:
            total = 0
        
        LIST = db.execute("SELECT * FROM Liabilities WHERE id = ? ORDER BY Owed DESC", session["user_id"])         
        return render_template('liabilities.html',LIST=LIST,total = total)
    else:
        total = db.execute("SELECT SUM(Owed) FROM Liabilities WHERE id = ?", session["user_id"])
        total = total[0]['SUM(Owed)']
        if total == None:
            total = 0
        
        LIST = db.execute("SELECT * FROM Liabilities WHERE id = ? ORDER BY Owed DESC", session["user_id"])         
        return render_template('liabilities.html',LIST=LIST,total = total)

@app.route('/save', methods=["GET", "POST"])  
def save():
    global month4
    if request.method == "POST":
        Target = request.form.get('Target')
        rows = db.execute("SELECT * FROM Target WHERE Month = ?",month4)
        if Target:
            if len(rows) == 1 or len(rows) == 0:
                db.execute("INSERT INTO Target (id, Month, Target) VALUES(?, ?, ?)", session["user_id"], month4, Target)
        Delete = request.form.get('Delete')
        if Delete != None:
            db.execute("DELETE FROM Target WHERE Month = ? AND id = ?",month4,session["user_id"])
        
        today = date.today()
        today = str(today)
        search = today[:-4]

        MONTH = request.form.get('month')
        if MONTH != None:
            MONTH = str(MONTH)
            MONTH = MONTH[-2:]
            if MONTH[:1] == '0':
                month4 = int(MONTH[-1:])
            else:
                month4 = int(MONTH)

        Previous = request.form.get('Previous')
        if Previous != None:
            month4 = int(month4) -1
        
        Next = request.form.get('Next')
        if Next != None:
            month4 = int(month4) +1


        if int(month4) > 12 or int(month4) < 1: #check if it overflow
            month4 = today[-4:-3]

        
            
      
        Month_full_name = calendar.month_name[int(month4)]
        search = search + str(month4)
        search = search + '%'
        
        Expenses = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        Expenses = Expenses[0]['SUM(expenses)']
        if Expenses == None:
            Expenses = 0
         
        target = db.execute("SELECT Target FROM Target WHERE id = ? AND Month = ?", session["user_id"], month4)
        difference = 0
        
        if target != []:
            target = target[0]['Target']
            if target != None:
                difference = int(target) - int(Expenses)
        else:
            target = 0
            
        return render_template('save.html',Month_full_name=Month_full_name, Expenses=Expenses, difference = difference, target=target)
    else:
        
        today = date.today()
        today = str(today)
        search = today[:-4]
        month4 = today[-4:-3]

        
        Month_full_name = calendar.month_name[int(month4)]
        search = search + str(month4)
        search = search + '%'
        
    
        Expenses = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ?", session["user_id"],search)
        Expenses = Expenses[0]['SUM(expenses)']
        if Expenses == None:
            Expenses = 0
        target = db.execute("SELECT Target FROM Target WHERE id = ? AND Month = ?", session["user_id"], month4)
        difference = 0
        
        if target != []:
            target = target[0]['Target']
            if target != None:
                difference = int(target) - int(Expenses)
        else:
            target = 0
        
        return render_template('save.html',Month_full_name=Month_full_name, Expenses=Expenses, difference = difference, target=target)







##@app.route('/success', methods = ['POST'])  
##def success():  
##    if request.method == 'POST':  
##        f = request.files['file']
##        f.save(f.filename)  
##        return render_template("acknowledgement.html", name = f.filename)  
  



if __name__ == '__main__':
    app.run()
