from flask import Flask, render_template, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "27eduCBA09"


#================================================================================================================================
def check_exists(username,password):
    result = False
    sqldbname = 'db/website.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    sqlcommand = "Select * from user where name = '"+username+"' and password = '"+password+"'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    if len(data) > 0:
        result = True
    conn.close()
    return result

def check_register(username, password):
    error = False
    sqldbname = 'db/website.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    sqlcommand = "Select * from user where name = '" + username + "'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    if len(data) > 0:
        error = True
    conn.close()
    return error

def insert_user(username, email, password):
    sqldbname = 'db/website.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = "Insert into user(name,email,password) values ('" + username + "', '" + username + "@gmail.com', '" + password + "')"
    cursor.execute(sqlcommand)
    conn.commit()
    conn.close()

def clothes_data(search_text):
    if(search_text != ''):
        sqldbname = 'db/clothes.db'
        conn = sqlite3.connect(slqdbname)
        cursor = conn.cursor()
        sqlcommand = "Select * from clothes where tags like '%" + search_text + "%'"

        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
    return data

#================================================================================================================================

@app.route("/")
def Index():
    username = ""
    return render_template("Index.html", username=username)

#================================================================================================================================

@app.route("/login")
def formlogin():
    return render_template("login.html")

@app.route("/login",methods=['POST'])
def login():
    error = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_exists(username, password):
            session['username'] = username
            return render_template("Index.html", username=session['username'])
        else:
            error = True
    return render_template("login.html", error=error)

#================================================================================================================================

@app.route("/register")
def registerform():
    return render_template("register.html")
@app.route("/register", methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    error = check_register(username, password)
    if not error:
        insert_user(username, email, password)
        return render_template("Index.html")
    else:
        return render_template("register.html", error = error)

@app.route("/search")
def search_clothes():
    return render_template("search.html")

#================================================================================================================================


if __name__ == '__main__':
    app.run()