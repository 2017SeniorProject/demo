from flask import Flask,request,session,redirect,url_for,render_template,flash
from .models import RecoEngine, User

app= Flask(__name__)
app.secret_key = "super secret key"

@app.route('/')
def index():
	return render_template("index.html")
	
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            render_template("notice.html",message='Your username must be at least one character.')
        elif len(password) < 5:
            render_template("notice.html",message='Your password must be at least 5 characters.')
        elif not User(username).register(password):
            render_template("notice.html",message='A user with that username already exists.')
        else:
            session['username'] = username
            return render_template("notice.html",message='Logged in.')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            return render_template("notice.html",message='Invalid password')
        else:
            session['username'] = username
            return render_template("notice.html",message='Logged in.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template("notice.html",message='Log out.')
    
	
@app.route("/near_you",methods=["GET","POST"])
def near_you():
	if request.method== "POST":
		location=request.form["division"]
		recommendation=RecoEngine.res_near_you(location)
		return render_template("show_near_you.html",recommendation=recommendation,division=location)
	return render_template("near_you.html")

@app.route("/by_month",methods=["GET","POST"])
def by_month():
	if request.method== "POST":
		#return "todo"
		location=request.form["division"]
		month=request.form["month"]
		recommendation=RecoEngine.res_by_month(location,month)
		return render_template("show_by_month.html",recommendation=recommendation,division=location,month=month)
	return render_template("by_month.html")

@app.route("/general_rec",methods=["GET","POST"])
def general_rec():
	if request.method=="POST":
		location=request.form['division']
		category=request.form["category"]
		session['division']=location
		session['category']=category
		recommendation=RecoEngine.res_general_rec(location,category)
		return render_template("show_general_rec.html",recommendation=recommendation,division=location,category=category)
	return render_template("general_rec.html")

@app.route("/show_similiar_search",methods=["GET"])
def show_similiar_search():
	location=session["division"]
	category=session["category"]
	recommendation=RecoEngine.res_similiar_search(location,category)
	return render_template("show_similiar_rec.html",recommendation=recommendation,division=location,category=category)

@app.route("/show_relating_search",methods=["GET"])
def show_relating_search():
	location=session["division"]
	category=session["category"]
	recommendation=RecoEngine.res_relating_search(location,category)
	return render_template("show_relating_rec.html",recommendation=recommendation,division=location,category=category)