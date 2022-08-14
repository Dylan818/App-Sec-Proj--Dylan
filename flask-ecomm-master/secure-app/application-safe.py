import uuid

from cs50 import SQL
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify
from datetime import datetime
import hashlib as hl
import re
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "2917dedc-f90d-4375-9beb-70e4814b1ced"
app.config['JWT_SECRET_KEY'] = '57716098c68c4f02bba85bbf82359be3'
Session(app)
jwt = JWTManager(app)
# Creates a connection to the database
db = SQL ( "sqlite:///data.db" )
iv = b'K?55\x08\xdf9\xb38|\x10\x9fe\xfbX\xd6'

def get_key():
    return b'\xc2*\xe2\xaf\xd0\x1f0rgd\x11D\x15iX\x7f#\x92\xb3\xee\x00\xb3\x85\xdb\x8e\xc7\xf2E\xbb\xef\xda\xfa'

def encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16, style="pkcs7"))
    return ciphertext

def decrypt(key, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), 16, style="pkcs7")
    return plaintext.decode('utf-8')

def e_test():
    msg = "Hello world"
    print(msg)
    emsg = encrypt(get_key(), msg.encode('utf-8'))
    print(emsg)

def d_test():
    msg = "Hello World"
    print(msg)
    emsg = encrypt(get_key(), msg.encode('utf-8'))
    print(decrypt(get_key(), emsg), "decrypted")
#state = db.execute("DROP TABLE users")
#state2 = db.execute("CREATE TABLE users(uid varchar(100) PRIMARY KEY, username varchar(20), password varchar(100), fname varchar(20), lname varchar(20), email varchar(40));")


@app.route("/webapi/getdetails/", methods=['GET', 'POST'])
@jwt_required()
def get_details():
    if 'user' in session:
        uid = session['uid']
        query = "SELECT username, email, fname, lname FROM users WHERE uid = '{}'".format(uid)
        details = db.execute(query)
        details[0]["email"] = decrypt(get_key(), details[0]["email"])
        details[0]["username"] = decrypt(get_key(), details[0]["username"])
        return jsonify(details)
    return jsonify(message="Not authorised!")


@app.route("/")
def index():
    shoes = db.execute("SELECT * FROM shoes ORDER BY team ASC")
    shoesLen = len(shoes)
    # Initialize variables
    cart = []
    shop = len(cart)
    totalItems = 0
    total = 0
    display = 0
    if 'user' in session:
        cart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(cart)
        for i in range(shop):
            total += cart[i]["SUM(subTotal)"]
            totalItems += cart[i]["SUM(qty)"]
        shoes = db.execute("SELECT * FROM shoes ORDER BY team ASC")
        shoesLen = len(shoes)
        return render_template ("index.html", shoppingCart=cart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totalItems, display=display, session=session )
    return render_template ( "index.html", shoes=shoes, shoppingCart=cart, shoesLen=shoesLen, shopLen=shop, total=total, totItems=totalItems, display=display)


@app.route("/buy/")
def buy():
    # Initialize shopping cart variables
    cart = []
    shopcartlen = len(cart)
    totalItems = 0
    total = 0
    display = 0
    qty = int(request.args.get('quantity'))
    if session:
        id = int(request.args.get('id'))
        items = db.execute("SELECT * FROM shoes WHERE id = :id", id=id)
        if(items[0]["onSale"] == 1):
            price = items[0]["onSalePrice"]
        else:
            price = items[0]["price"]
        team = items[0]["team"]
        image = items[0]["image"]
        subTotal = qty * price
        db.execute("INSERT INTO cart (id, qty, team, image, price, subTotal) VALUES (:id, :qty, :team, :image, :price, :subTotal)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)
        cart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopcartlen = len(cart)
        for i in range(shopcartlen):
            total += cart[i]["SUM(subTotal)"]
            totalItems += cart[i]["SUM(qty)"]
        shoes = db.execute("SELECT * FROM shoes ORDER BY team ASC")
        shoesLen = len(shoes)
        return render_template ("index.html", shoppingCart=cart, shoes=shoes, shopLen=shopcartlen, shoesLen=shoesLen, total=total, totItems=totalItems, display=display, session=session )


@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        db.execute("DELETE FROM cart WHERE id = :id", id=id)
        # Select info of selected shirt from database
        goods = db.execute("SELECT * FROM shoes WHERE id = :id", id=id)
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.execute("INSERT INTO cart (id, qty, team, image, price, subTotal) VALUES (:id, :qty, :team, :image, :price, :subTotal)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Go back to cart page
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('continent'):
        query = request.args.get('continent')
        shoes = db.execute("SELECT * FROM shoes WHERE continent = :query ORDER BY team ASC", query=query )
    if request.args.get('sale'):
        query = request.args.get('sale')
        shoes = db.execute("SELECT * FROM shoes WHERE onSale = :query ORDER BY team ASC", query=query)
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shoes = db.execute("SELECT * FROM shoes WHERE id = :query ORDER BY team ASC", query=query)
    if request.args.get('kind'):
        query = request.args.get('kind')
        shoes = db.execute("SELECT * FROM shoes WHERE kind = :query ORDER BY team ASC", query=query)
    if request.args.get('price'):
        query = request.args.get('price')
        shoes = db.execute("SELECT * FROM shoes ORDER BY onSalePrice ASC")
    shoesLen = len(shoes)
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Rebuild shopping cart
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Render filtered view
        return render_template ("index.html", shoppingCart=shoppingCart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totItems, display=display, session=session )
    # Render filtered view
    return render_template ( "index.html", shoes=shoes, shoppingCart=shoppingCart, shoesLen=shoesLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/checkout/")
def checkout():
    order = db.execute("SELECT * from cart")
    # Update purchase history of current customer
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, team, image, quantity) VALUES(:uid, :id, :team, :image, :quantity)", uid=session["uid"], id=item["id"], team=item["team"], image=item["image"], quantity=item["qty"] )
    # Clear shopping cart
    db.execute("DELETE from cart")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Redirect to home page
    return redirect('/')


@app.route("/removefromcart/", methods=["GET"])
def removefromcart():
    removed = int(request.args.get("id"))
    db.execute("DELETE from cart WHERE id=:id", id=removed)
    totalItems= 0
    total=0
    shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
    shop = len(shoppingCart)
    for i in range(shop):
        total += shoppingCart[i]["SUM(subTotal)"]
        totalItems += shoppingCart[i]["SUM(qty)"]
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shop, total=total, totItems=totalItems,  session=session)


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # Render log in page
    return render_template("new.html")


def validate_username(user_input):
    pattern = r"\d|[a-z]|[A-Z]"
    if re.search(pattern, user_input):
        x = re.findall(pattern, user_input)
        print(x)
        if len(x) == len(user_input):
            print("h1")
            return True
        else:
            return False

    else:
        print("Not found")
        return False


def validate_password(user_input):
    pattern = "\d|[a-z]|[A-Z][!@#$]"
    if re.search(pattern, user_input):
        x = re.findall(pattern, user_input)
        if len(x) == len(user_input):
            print("h1")
            return True
        else:
            return False
    else:
        print("Not found")
        return False


@app.route("/loggedapi/", methods=["POST"] )
def loggedapi():
    if request.is_json:
        user = request.json["username"]
        pwd = hashing_pwsd(request.json["password"])
    else:
        user= request.form['username']
        pwd = hashing_pwsd(request.form['password'])
    request_query = "SELECT * FROM users WHERE username = :username AND password = :password"
    if user == "" or pwd == "" or validate_username(user) is False or validate_password(request.form["password"]) is False:
        return render_template ( "login.html", msg="Wrong username or password." )
    user = encrypt(get_key(), user.encode('utf-8'))
    rows = db.execute(request_query, username = user, password = pwd)
    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now( )
        session['uid'] = rows[0]["uid"]
        print(session['uid'])
    if 'user' in session:
        access_token = create_access_token(identity=session['uid'])
        return jsonify(message="logged", access_token = access_token)
    return jsonify(message="Invalid login!")


@app.route("/logged/", methods=["POST"] )
def logged():
    user = request.form["username"].lower()
    pwd = hashing_pwsd(request.form["password"])
    request_query = "SELECT * FROM users WHERE username = :username AND password = :password"
    if user == "" or pwd == "" or validate_username(user) is False or validate_password(request.form["password"]) is False:
        return render_template ( "login.html", msg="Wrong username or password." )
    user = encrypt(get_key(), user.encode('utf-8'))
    rows = db.execute(request_query, username = user, password = pwd)
    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now( )
        session['uid'] = rows[0]["uid"]
        access_token = create_access_token(identity=session['uid'])
        session['token'] = access_token
        print(session['uid'])
    # Redirect to Home Page
    if 'user' in session:
        return redirect ( "/" )
    # If username is not in the database return the log in page
    return render_template ( "login.html", msg="Wrong username or password." )


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all shoes ever bought by current user
    myshoes = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myshoesLen = len(myshoes)
    # Render table with shopping history of current user
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myshoes=myshoes, myshoesLen=myshoesLen)


@app.route("/logout/")
def logout():
    # clear shopping cart
    db.execute("DELETE from cart")
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


def hashing_pwsd(pwsd):
        return hl.pbkdf2_hmac('sha256', str(pwsd).encode(), b'salt', 100000).hex()


@app.route("/register/", methods=["POST"] )
def registration():
    username = str(request.form["username"]).lower()
    password = str(hashing_pwsd(request.form["password"]))
    confirm = hashing_pwsd(request.form["confirm"])
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    uid = str(uuid.uuid4())
    if password == confirm:
        if validate_username(username) is False:
            return render_template ( "new.html", msg="Invalid username!")
        elif validate_password(request.form["password"]) is False:
            return render_template ( "new.html", msg="Invalid password!" )
        rows = db.execute( "SELECT * FROM users WHERE username = :username ", username = username )
        if len( rows ) > 0:
            return render_template ( "new.html", msg="Username already exists!" )
        email = encrypt(get_key(), email.encode('utf-8'))
        username = encrypt(get_key(), username.encode('utf-8'))
        db.execute ( "INSERT INTO users (uid, username, password, fname, lname, email) VALUES (:uid, :username, :password, :fname, :lname, :email)",
                        uid = uid, username=username, password=password, fname=fname, lname=lname, email=email )
    else:
        return render_template ( "new.html", msg="Password must Match!")
    return render_template ( "login.html" )


@app.route("/cart/")
def cart():
    if 'user' in session:
        # Clear shopping cart variables
        totItems, total, display = 0, 0, 0
        # Grab info currently in database
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        # Get variable values
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


# @app.errorhandler(404)
# def pageNotFound( e ):
#     if 'user' in session:
#         return render_template ( "404.html", session=session )
#     return render_template ( "404.html" ), 404

def show_sql():
    rows = db.execute("SELECT * from USERS")
    rows_shirt = db.execute("SELECT * FROM Shoes")
    print(rows)
    print(rows_shirt)

def delete_shirts():
    db.execute("DELETE FROM shoes WHERE team IN ('River Plate','Boca Juniors', 'FC Barcelona','Real Madrid', 'Juventus','Milan','Manchester City','Manchester United','Flamengo','Corinthians');")

if __name__ == "__main__":
   e_test()
   d_test()
   delete_shirts()
   show_sql()
   app.run( host='0.0.0.0', port=8080 )
