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
import os
from xml.dom.minidom import parse, parseString


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "2917dedc-f90d-4375-9beb-70e4814b1ced"
app.config['JWT_SECRET_KEY'] = '57716098c68c4f02bba85bbf82359be3'
Session(app)
jwt = JWTManager(app)
if os.name != "nt":
    os.chdir(os.path.dirname(__file__))
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
    shoes = db.execute("SELECT * FROM shoes ORDER BY country ASC")
    shoesLen = len(shoes)
    cart = []
    shop = len(cart)
    totalItems = 0
    total = 0
    display = 0
    if 'user' in session:
        cart = db.execute("SELECT country, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY country")
        shopLen = len(cart)
        for i in range(shop):
            total += cart[i]["SUM(subTotal)"]
            totalItems += cart[i]["SUM(qty)"]
        shoes = db.execute("SELECT * FROM shoes ORDER BY country ASC")
        shoesLen = len(shoes)
        return render_template ("index.html", shoppingCart=cart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totalItems, display=display, session=session )
    return render_template ( "index.html", shoes=shoes, shoppingCart=cart, shoesLen=shoesLen, shopLen=shop, total=total, totItems=totalItems, display=display)


@app.route("/buy/", methods = ["POST"])
def buy():
    cart = []
    totalItems = 0
    total = 0
    display = 0
    qty = int(request.form['quantity'])
    if session:
        id = int(request.form['id'])
        cust_id = session['uid']
        items = db.execute("SELECT * FROM shoes WHERE id = :id", id=id)
        if(items[0]["onSale"] == 1):
            price = items[0]["onSalePrice"]
        else:
            price = items[0]["price"]
        country = items[0]["country"]
        image = items[0]["image"]
        subTotal = qty * price
        db.execute("INSERT INTO cart (id, qty, country, image, price, subTotal, cust_id) VALUES (:id, :qty, :country, :image, :price, :subTotal, :cust_id)", id=id, qty=qty, country=country, image=image, price=price, subTotal=subTotal, cust_id = cust_id)
        cart = db.execute("SELECT country, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY country")
        shopcartlen = len(cart)
        for i in range(shopcartlen):
            total += cart[i]["SUM(subTotal)"]
            totalItems += cart[i]["SUM(qty)"]
        shoes = db.execute("SELECT * FROM shoes ORDER BY country ASC")
        shoesLen = len(shoes)
        return render_template ("index.html", shoppingCart=cart, shoes=shoes, shopLen=shopcartlen, shoesLen=shoesLen, total=total, totItems=totalItems, session=session )


@app.route("/update/")
def update():
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        id = int(request.args.get('id'))
        cust_id = session['uid']
        db.execute("DELETE FROM cart WHERE id = :id AND cust_id = :cust_id", id=id, cust_id = cust_id)
        goods = db.execute("SELECT * FROM shoes WHERE id = :id", id=id)
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        country = goods[0]["country"]
        image = goods[0]["image"]
        subTotal = qty * price
        db.execute("INSERT INTO cart (id, qty, country, image, price, subTotal, cust_id) VALUES (:id, :qty, :country, :image, :price, :subTotal, :cust_id)", id=id, qty=qty, country=country, image=image, price=price, subTotal=subTotal, cust_id = cust_id)
        shoppingCart = db.execute("SELECT country, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY country")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('continent'):
        query = request.args.get('continent')
        shoes = db.execute("SELECT * FROM shoes WHERE continent = :query ORDER BY country ASC", query=query )
    if request.args.get('sale'):
        query = request.args.get('sale')
        shoes = db.execute("SELECT * FROM shoes WHERE onSale = :query ORDER BY country ASC", query=query)
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shoes = db.execute("SELECT * FROM shoes WHERE id = :query ORDER BY country ASC", query=query)
    if request.args.get('price'):
        query = request.args.get('price')
        shoes = db.execute("SELECT * FROM shoes ORDER BY onSalePrice ASC")
    shoesLen = len(shoes)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        cust_id = session['uid']
        shoppingCart = db.execute("SELECT country, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE cust_id = :cust_id GROUP BY country", cust_id = cust_id)
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template ("index.html", shoppingCart=shoppingCart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ( "index.html", shoes=shoes, shoppingCart=shoppingCart, shoesLen=shoesLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/checkout/")
def checkout():
    cust_id = session['uid']
    order = db.execute("SELECT * from cart WHERE cust_id = :cust_id", cust_id = cust_id)
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, country, image, quantity) VALUES(:uid, :id, :country, :image, :quantity)", uid=session["uid"], id=item["id"], country=item["country"], image=item["image"], quantity=item["qty"] )
    db.execute("DELETE from cart WHERE cust_id = :cust_id", cust_id = cust_id)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    return redirect('/thankyou')

@app.route("/thankyou/")
def thankyou():
    document = parse("thankyou.svg")
    with open("thankyou.svg") as file:
        document = parse(file)
        render_template('thankyou.html' , document=document)


@app.route("/removefromcart/", methods=["GET"])
def removefromcart():
    removed = int(request.args.get("id"))
    cust_id = session['uid']
    db.execute("DELETE from cart WHERE id=:id AND cust_id = :cust_id", id=removed, cust_id = cust_id)
    totalItems= 0
    total=0
    shoppingCart = db.execute("SELECT country, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE cust_id = :cust_id GROUP BY country", cust_id = cust_id)
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
    if 'user' in session:
        return redirect ( "/" )
    return render_template ( "login.html", msg="Wrong username or password." )


@app.route("/history/")
def history():
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    myshoes = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myshoesLen = len(myshoes)
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myshoes=myshoes, myshoesLen=myshoesLen)


@app.route("/logout/")
def logout():
    db.execute("DELETE from cart")
    session.clear()
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
        rows = db.execute( "SELECT * FROM users WHERE username = :username ", username = encrypt(get_key(), username.encode('utf-8')) )
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
        totItems, total, display = 0, 0, 0
        cust_id = session['uid']
        shoppingCart = db.execute("SELECT country, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE cust_id = (:cust_id)GROUP BY country;", cust_id = cust_id)
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


def show_sql():
    rows = db.execute("SELECT * from USERS;")
    rows_shoe = db.execute("SELECT * FROM Shoes;")
    rows_shoes = db.execute("SELECT * FROM cart;")
    rows_purchases = db.execute("SELECT * FROM purchases;")
    print(rows)
    print(rows_shoe)
    print(rows_shoes)
    print(rows_purchases)

def add_row():
    db.execute("ALTER TABLE cart ADD cust_id VARCHAR (100);")

if __name__ == "__main__":
   show_sql()
   app.run( host='0.0.0.0', port=90)
