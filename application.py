import os

from flask import Flask, session, render_template, jsonify, request, redirect, flash, url_for, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from auth import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
# Set the secret key to some random bytes. Keep this really secret!
#app.secret_key = os.getenv("SECRET_KEY")
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
#Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	page_title = 'Home'
	data = {
	"page_title":page_title
	}
	#init_db()

	keywords = request.args.get('search')
	data['search']=keywords
	if keywords is not None and keywords !='':
		keywords = '%'+keywords+'%'
		books = db.execute("SELECT * FROM books WHERE title like :s or author like :s  or isbn like :s ",{"s":keywords}).fetchall()
		if books:
			data['books']= books
		else:
			data['no_result']='No result found for these keywords.'

	return render_template('index.html',data=data)

@app.route('/subscribe',methods=['GET','POST'])
def subscribe():
	page_title = 'Subscribe'
	data = {
	"page_title":page_title
	}
	# redirect if already logged in
	if session.get('user_id'):
		return redirect('/')

	if request.method == 'POST':
		username = request.form.get('username')
		email = request.form.get('email')
		passwd = request.form.get('passwd')
		conf_passwd = request.form.get('conf_passwd')
		# Validating form data
		data_valid = True
		if username == '':
			data['errUSR']='Username can not be blank.'
			data_valid = False
		if db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone():
			data['errUSR']='Username unavailable.'
			data_valid = False
		if email == '':
			data['errMail']='Email address can not be blank.'
			data_valid = False
		try:
			char=email.index('@')
			char=email.index('.')
		except ValueError:
			data['errMail']='Email address invalid.'
			data_valid = False
		if db.execute("SELECT email FROM users WHERE email=:email",{"email":email}).fetchone():
			data['errMail']='Email already registered.'
			data_valid = False
		if passwd != conf_passwd:
			data['errPWD']='Passwords do not match.'
			data_valid = False
		if len(passwd)<6:
			data['errPWD']='Password too short.'
			data_valid = False
		# inserting data after validation
		if data_valid is True:
			db.execute("INSERT INTO users (username,email,passwd,auth_level) VALUES(:username,:email,:passwd,:auth_level)",params={"username":username,"email":email,"passwd":pass_hashing(passwd),"auth_level":1})
			db.commit()
			# setting sessions variables
			res = db.execute("SELECT * FROM users WHERE username=:username",{"username":username}).fetchone()
			session['username'] = username
			session['auth_level'] = res.auth_level
			session['user_id'] = res.id
			return redirect('/')
		
	data['form']= request.form

	return render_template('subscribe.html',data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
	page_title = 'Login'
	data = {
	"page_title":page_title
	}
	# redirect if already logged in
	if session.get('user_id'):
		return redirect('/')
	if request.method == 'POST':
		username = request.form.get('username')
		res = db.execute("SELECT * FROM users WHERE username=:username",{"username":username}).fetchone()
		if res != None:
			if(res.username == username):
				passwd = request.form.get('passwd')
				if(pass_verify(res.passwd,passwd)):
					session['username'] = username
					session['auth_level'] = res.auth_level
					session['user_id'] = res.id
					return redirect('/')
				else:
					#data['errPWD']= 'Password incorrect'
					data['msg_error']= 'Username or Password incorrect'
		else:
			#data['errUSR']= 'Username does not exist !'
			data['msg_error']= 'Username or Password incorrect'
	
	data['form']= request.form
	return render_template("login.html",data=data)

@app.route('/logout')
def logout():
	#session.clear()
	session.pop('username',None)
	session.pop('auth_level',None)
	session.pop('user_id',None)
	return redirect('/login')

@app.route('/find_book')
def find_book():
	page_title = 'FInd a book'
	data = {
	"page_title":page_title
	}
	return render_template("layout.html",data=data)

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
	page_title = 'Book'
	data = {
	"page_title":page_title
	}
	# Getting book details
	data['book']=db.execute("SELECT * FROM books WHERE id=:id",{"id":id}).fetchone()
	if data['book'] is None:
		data['msg_error']='The book you are trying to find is not available.'
		return render_template("error.html", data=data)
	isbn = data['book'].isbn
	# Checking if the user has just posted a review
	if request.method == 'POST':
		try:
			isbn = data['book'].isbn
			user_id = session['user_id']
			heading = request.form.get('heading')
			comments = request.form.get('comments')
			rating =  request.form.get('rating')
			if float(rating) >=1:
				# looking for existing user rating
				my_rating = db.execute('SELECT * FROM reviews WHERE isbn=:isbn AND user_id=:user_id',params={"isbn":data['book'].isbn,"user_id":session.get('user_id')}).fetchone()
				if my_rating is None:
					db.execute('INSERT INTO reviews (isbn,user_id,heading,comments,rating) VALUES(:isbn,:user_id,:heading,:comments,:rating)'\
					,params={"isbn":isbn,"user_id":user_id,"heading":heading,"comments":comments,"rating":rating})
					db.commit()
				else:
					db.execute('UPDATE reviews set heading=:heading,comments=:comments,rating=:rating WHERE isbn=:isbn AND user_id=:user_id'\
					,params={"heading":heading,"comments":comments,"rating":rating,"isbn":isbn,"user_id":user_id})
					db.commit()
			else:
				data['msg_error']='You must choose a rate and set a heading.'
		except KeyError:
			data['msg_error']='You must be logged in.'
	
	# getting general reviews ratings
	book_rating = db.execute('SELECT avg(rating) as rating FROM reviews WHERE isbn=:isbn',params={"isbn":data['book'].isbn}).fetchone()
	try:
		data['book_rating']= float(book_rating.rating)
	except TypeError:
		data['book_rating']= float(0)		
	# Getting user's review for that book
	data['book_rating_stars'] = format_rating(data['book_rating'])
	my_rating = db.execute('SELECT * FROM reviews WHERE isbn=:isbn AND user_id=:user_id',params={"isbn":data['book'].isbn,"user_id":session.get('user_id')}).fetchone()
	data['my_rating'] = my_rating
	try:
		data['my_rating_stars'] = format_rating(float(my_rating.rating),'myrating')
	except TypeError:
		data['my_rating_stars'] = format_rating(float(0),'myrating')
	except AttributeError:
		data['my_rating_stars'] = format_rating(float(0),'myrating')
	try:
		goodread_review = requests.get('https://www.goodreads.com/book/review_counts.json',params={"key":'xpF7YDthAftyDazUNvFWQ',"isbns":isbn}).json()
		if goodread_review is not None:
			data['goodread_review'] = goodread_review
			data['goodread_rating_stars'] = format_rating(goodread_review['books'][0]['average_rating'])
	except:
		data['goodread_review']= None
		data['goodread_rating_stars']= None
		data['msg_warning']='Could not get reviews from goodread'
	
	return render_template("book.html",data=data)

def init_db():
	# Creating tables structure
	with open('db_sql.sql') as fichier:
		lignes = fichier.read().split(';')
		for ligne in lignes:
			if ligne !='':
				db.execute(ligne)
				db.commit()
		db.commit()
	# Creating default admin
	try:
		default_adm_pass = pass_hashing('Pass0321')
		db.execute("INSERT INTO users (id,username,email,passwd,auth_level) VALUES(1,'admin','admin@mail.com',:passwd,4)",{"passwd":default_adm_pass})
		db.commit()
	except:
		pass

def format_rating(rate,css=''):
	try:
		rate = float(rate)
	except:
		return ''
	rating_stars = ''
	decimal = str(rate).split('.')[1]
	for i in range(int(rate)):
		rating_stars +='<span class="fa fa-star checked '+css+'" data-rate="'+str(i+1)+'"></span>\n'
	if int(decimal[0]) >= 5: # sliced to be sure that we take the first digit if there is more than one
		rating_stars +='<span class="fa fa-star-half checked '+css+'" data-rate="'+str(i+1)+'"></span>\n'
		for i in range(int(rate+1),5):
			rating_stars +='<span class="fa fa-star-o unchecked '+css+'" data-rate="'+str(i+1)+'"></span>\n'
	else:
		for i in range(int(rate),5):
			rating_stars +='<span class="fa fa-star-o unchecked '+css+'" data-rate="'+str(i+1)+'"></span>\n'
	return rating_stars
# https://www.goodreads.com/book/review_counts.json?key=xpF7YDthAftyDazUNvFWQ&isbns=1416949658
"""
import requests
res = requests.get('https://www.goodreads.com/book/review_counts.json',params=["key":key,"isbns":isbn])
print(res.json())

"""	
