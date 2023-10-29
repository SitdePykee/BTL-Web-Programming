from flask import Flask, render_template, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "27eduCBA09"


#================================================================================================================================
def check_exists(username,password):
    result = False
    sqldbname = 'db/clothes.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    sqlcommand = "Select * from user where username = '"+username+"' and password = '"+password+"'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    if len(data) > 0:
        result = True
    conn.close()
    return result

def check_register(username, password):
    error = False
    sqldbname = 'db/clothes.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    sqlcommand = "Select * from user where username = '" + username + "'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    if len(data) > 0:
        error = True
    conn.close()
    return error

def insert_user(username, email, password):
    sqldbname = 'db/clothes.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = "Insert into user(username,gmail,password) values ('" + username + "', '"+ email +"', '" + password + "')"
    cursor.execute(sqlcommand)
    conn.commit()
    conn.close()

def get_clothes_data(id):
    sqldbname = 'db/clothes.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = "Select * from clothes where id = '"+ str(id) +"'"
    cursor.execute(sqlcommand)

    data = cursor.fetchone()
    return data

def search_clothes(search_text):
    if search_text != "":
        sqldbname = 'db/clothes.db'
        conn = sqlite3.connect(sqldbname)
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
    data = []
    items_per_page = 12
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    for i in range(48):
        data.append(get_clothes_data(i + 1))
        current_page_items = data[start_index:end_index]
        total_pages = len(data) // items_per_page + (1 if len(data) % items_per_page > 0 else 0)

    return render_template("Index.html", username=username, clothes = current_page_items,
                           total_pages = total_pages, current_page = page)

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
            data = []
            for i in range(12):
                data.append(get_clothes_data(i + 1))
            return render_template("Index.html", username=session['username'], clothes = data)
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
        data = []
        for i in range(12):
            data.append(get_clothes_data(i + 1))
        insert_user(username, email, password)
        return render_template("Index.html", clothes = data)
    else:
        return render_template("register.html", error = error)

@app.route("/search")
def search_clothes_form():
    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search_result():
    search_text = request.form['search_text']
    data = search_clothes(search_text)
    return render_template("search.html", data = data, search_text = search_text)


#================================================================================================================================


if __name__ == '__main__':
    app.run()