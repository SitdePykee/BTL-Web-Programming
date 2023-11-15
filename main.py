from flask import Flask, render_template, request, session, redirect, url_for, jsonify
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
        sqlcommand = "Select * from clothes where tags like '%" + search_text + "%' or product like '%" + search_text + "%' or brand like '%" + search_text + "%'"

        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
    return data

def get_items_default():
    data = []
    items_per_page = 12
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * items_per_page

    sqldbname = 'db/clothes.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = "SELECT MAX(id) FROM clothes"
    cursor.execute(sqlcommand)
    max_item = cursor.fetchone()
    cursor.close()
    for i in range(max_item[0]):
        data.append(get_clothes_data(i + 1))

    total_pages = len(data) // items_per_page + (1 if len(data) % items_per_page > 0 else 0)
    current_page_items = data[start_index:start_index + min(items_per_page, len(data) - start_index)]
    number_of_item = len(current_page_items)
    return current_page_items, total_pages, page, number_of_item

def get_items_with_categories(category):
    data = []
    items_per_page = 12
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * items_per_page

    sqldbname = 'db/clothes.db'
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = "Select * from clothes where tags like '%" + category + "%'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()

    total_pages = len(data) // items_per_page + (1 if len(data) % items_per_page > 0 else 0)
    current_page_items = data[start_index:start_index + min(items_per_page, len(data) - start_index)]
    number_of_item = len(current_page_items)
    return current_page_items, total_pages, page, number_of_item

#================================================================================================================================

@app.route("/")
def Index():
    current_page_items, total_pages, page, number_of_item = get_items_default()
    if 'username' in session:
        return render_template("logged-in-index.html", username=session['username'],
                                   clothes = current_page_items,total_pages = total_pages, current_page = page,
                                   number_of_item = number_of_item)
    else:
        return render_template("Index.html",clothes = current_page_items,
                           total_pages = total_pages, current_page = page, number_of_item = number_of_item)

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
            current_page_items, total_pages, page, number_of_item = get_items_default()
            return render_template("logged-in-index.html", username=session['username'],
                                   clothes = current_page_items,total_pages = total_pages, current_page = page,
                                   number_of_item = number_of_item)
        else:
            error = True
    return render_template("login.html", error=error)

#================================================================================================================================
@app.route("/logout")
def log_out():
    session.clear()
    return redirect(url_for('Index'))
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
        current_page_items, total_pages, page, number_of_item = get_items_default()
        return render_template("Index.html",clothes = current_page_items,total_pages = total_pages,
                               current_page = page, number_of_item = number_of_item)
    else:
        return render_template("register.html", error = error)
#================================================================================================================================
@app.route("/search")
def search_clothes_form():
    if 'username' in session:
        return render_template("logged-in-search.html", username=session['username'])
    else:
        return render_template("search.html")

@app.route("/search", methods=["POST"])
def search_result():
    search_text = request.form['search_text']
    data = search_clothes(search_text)
    if 'username' in session:
        return render_template("logged-in-search.html", username=session['username'],
                               data = data, search_text = search_text)
    else:
        return render_template("search.html", data = data, search_text = search_text)
#================================================================================================================================
@app.route("/item")
def item_w_category():
    category = request.args.get('category')
    current_page_items, total_pages, page, number_of_item = get_items_with_categories(category)
    if 'username' in session:
        return render_template("logged-in-item.html",clothes = current_page_items, username=session['username'],
                                total_pages = total_pages, current_page = page, number_of_item = number_of_item, category = category)
    else:
        return render_template("item.html", clothes=current_page_items,
                               total_pages=total_pages, current_page=page, number_of_item=number_of_item, category = category)

#================================================================================================================================
@app.route("/product")
def display_product():
    id = request.args.get('id')
    clothes = get_clothes_data(id)
    if("username" in session):
        return render_template("logged-in-product.html", clothes = clothes)
    else:
        return render_template("product.html", clothes=clothes)

#================================================================================================================================

@app.route("/cart")
def display_cart():

    return render_template("cart.html")

@app.route('/cart/add', methods=['POST','GET'])
def add_to_cart():
    # Lấy giá trị id, size và quantity từ dữ liệu gửi lên
    data = request.json
    id = data['id']
    clothes = get_clothes_data(id)
    clothes_dict = {
        "id": id,
        "name": clothes[1],
        "img": clothes[3],
        "price": clothes[4],
        "quantity": int(data['quantity']),
        "size": data['size']
    }

    print(clothes_dict)

    cart = session.get('cart', [])
    found = False;
    for item in cart:
        if item["id"] == id:
            item["quantity"] = int(item["quantity"])
            if "quantity" not in item:
                item["quantity"] = 0  # Gán giá trị ban đầu
            item["quantity"] += int(clothes_dict["quantity"])
            found = True
            break
    if not found:
        cart.append(clothes_dict)
    session['cart'] = cart

    response = {'message': 'Thêm vào giỏ hàng thành công'}
    return render_template("cart.html")

@app.route("/cart/update", methods=['POST'])
def update_cart():
    cart = session['cart']
    data = request.json
    t = data["type"]
    new_quantity = data["quantity"]
    if t == "UPDATE":
        for i in cart:
            if i['id'] == data["id"]:
                i['quantity'] = new_quantity
    elif t == "DELETE_ONE":
        for i in cart:
            if i['id'] == data["id"]:
                cart.remove(i)
    else:
        cart.clear()
    session['cart'] = cart

    return render_template("cart.html")
#================================================================================================================================
@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

#================================================================================================================================


if __name__ == '__main__':
    app.run()