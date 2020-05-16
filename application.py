import os

from flask import Flask, session, render_template, jsonify, request, redirect, flash, url_for, request, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from auth import *
from functions import *
# explicit importation of the decorator fuction for login check
from functions import require_login

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

per_page=25
off_set=0

@app.route("/")
@require_login
def index():
	page_title = 'Home'
	data = {
	"page_title":page_title
	}
	#init_db()
	# Calculating off_set
	page_arg = request.args.get('page')
	if page_arg is not None:
		actual_page = int(page_arg)
	else:
		actual_page= 1
	off_set = (per_page*int(actual_page))-per_page
	
	# initializing res_count
	res_count =0
	
	keywords = request.args.get('search')
	data['search']=keywords
	if keywords is not None and keywords !='':
		data['url_params'] = '&search='+keywords
		keywords = '%'+keywords+'%'
		books = db.execute("SELECT * FROM books WHERE title ilike :s or author ilike :s  or isbn ilike :s LIMIT :per_page OFFSET :off_set",{"s":keywords,"per_page":per_page,"off_set":off_set}).fetchall()
		if books:
			data['books']= books
			# pagination
			res_count = db.execute("SELECT count(*) as total FROM books WHERE title ilike :s or author ilike :s  or isbn ilike :s ",{"s":keywords}).fetchone().total
			data['pagination']=paginate(res_count,per_page)
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
@require_login
def logout():
	#session.clear()
	session.pop('username',None)
	session.pop('auth_level',None)
	session.pop('user_id',None)
	return redirect('/login')

@app.route('/list_books')
@app.route('/list_books/page/<int:page>')
@require_login
def list_books(page='1'):
	page_title = 'Find a book'
	data = {
	"page_title":page_title
	}
	# Calculating off_set
	page_arg = request.args.get('page')
	if page_arg is not None:
		actual_page = int(page_arg)
	else:
		actual_page= 1
	off_set = (per_page*int(actual_page))-per_page
	
	# initializing res_count
	res_count =0
	keywords = request.args.get('search')
	data['search']=keywords
	if keywords is not None and keywords !='':
		data['url_params'] = '&search='+keywords
		keywords = '%'+keywords+'%'
		books = db.execute("SELECT * FROM books WHERE title ilike :s or author ilike :s  or isbn ilike :s LIMIT :per_page OFFSET :off_set",{"s":keywords,"per_page":per_page,"off_set":off_set}).fetchall()
		if books:
			data['books']= books
			# pagination
			res_count = db.execute("SELECT count(*) as total FROM books WHERE title ilike :s or author ilike :s  or isbn ilike :s ",{"s":keywords}).fetchone().total
			
		else:
			data['no_result']='No result found for these keywords.'
	else:
		books = db.execute("SELECT * FROM books LIMIT :per_page OFFSET :off_set",{"per_page":per_page,"off_set":off_set}).fetchall()
		if books:
			data['books']= books
		else:
			data['no_result']='No books in the database yet.'
		# pagination
		res_count = db.execute("SELECT count(*) as total FROM books").fetchone().total
	
	data['pagination']=paginate(res_count,per_page)
	
	return render_template("book_list.html",data=data)

@app.route('/mybooks')
@require_login
def mybooks():
	page_title = 'My rated books'
	data = {
	"page_title":page_title
	}
	user_id = session.get('user_id')	
	# Calculating off_set
	page_arg = request.args.get('page')
	if page_arg is not None:
		actual_page = int(page_arg)
	else:
		actual_page= 1
	off_set = (per_page*int(actual_page))-per_page
	
	# initializing res_count
	res_count =0
	keywords = request.args.get('search')
	data['search']=keywords
	if keywords is not None and keywords !='':
		data['url_params'] = '&search='+keywords
		keywords = '%'+keywords+'%'
		books = db.execute("Select r.id as review_id,r.isbn,r.user_id,r.heading,r.comments,r.rating,b.id as book_id,b.title,b.author,b.year from reviews r,books b\
		WHERE r.isbn=b.isbn AND r.user_id=:user_id AND (title ilike :s or author ilike :s  or r.isbn ilike :s) LIMIT :per_page OFFSET :off_set",{"user_id":user_id,"s":keywords,"per_page":per_page,"off_set":off_set}).fetchall()
		if books:
			data['books']= books
			# pagination
			res_count = db.execute("Select count(*) as total from reviews r,books b WHERE r.isbn=b.isbn AND r.user_id=:user_id AND (title ilike :s or author ilike :s  or r.isbn ilike :s)",{"user_id":user_id,"s":keywords}).fetchone().total
			
		else:
			data['no_result']='No result found for these keywords.'
	else:
		books = db.execute("Select r.id as review_id,r.isbn,r.user_id,r.heading,r.comments,r.rating,b.id as book_id,b.title,b.author,b.year from reviews r,books b\
		WHERE r.isbn=b.isbn AND r.user_id=:user_id ORDER BY r.id DESC LIMIT :per_page OFFSET :off_set",{"user_id":user_id,"per_page":per_page,"off_set":off_set}).fetchall()
		if books:
			data['books']= books
		else:
			data['no_result']='You have not yet rated any book.'
		# pagination
		res_count = db.execute("Select count(*) as total from reviews r, books b WHERE r.isbn=b.isbn AND r.user_id=:user_id",{"user_id":user_id}).fetchone().total
	
	data['pagination']=paginate(res_count,per_page)
	
	return render_template("my_books.html",data=data)

@app.route('/book/<int:id>', methods=['GET','POST'])
@require_login
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


@app.route('/api/<isbn>')
def api(isbn):
	book = db.execute('SELECT * FROM books WHERE isbn=:isbn',params={"isbn":isbn}).fetchone()
	if book is None:
		return abort(404)
	rev_count = db.execute('SELECT count(*) as count FROM reviews WHERE isbn=:isbn',params={"isbn":isbn}).fetchone()
	rev_score = db.execute('SELECT avg(rating) as avg_score FROM reviews WHERE isbn=:isbn',params={"isbn":isbn}).fetchone()
	data = {
		"title":book.title,
		"author":book.author,
		"year":book.year,
		"isbn":book.isbn,
		"review_count":rev_count.count,
		"average_score":rev_score.avg_score,
	}
	return jsonify(data)
