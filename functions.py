import os
import functools
from flask import jsonify, request, redirect, session
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def require_login(func):
	"""Decorator function to check if user is logged in"""
	@functools.wraps(func) # makes the function keeps it's identity
	def wrapper_login_check(*args, **kwargs):
		# check for session's details
		if session.get('user_id') is None:
			return redirect('/login')
		# Then run de called funcction after the check
		called_function = func(*args, **kwargs)
		return called_function
	return wrapper_login_check

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
	
def pagination_format(page_obj):
	index = page_obj['page']
	max_index= int(page_obj['total'])
	start_index= index - 3 if index >=3 else 0
	end_index = index + 3 if index <= max_index - 3 else max_index
	page_range = list(page_obj['page_range'])[int(start_index):int(end_index)]
	return page_range

def paginate(res_count,per_page):
	page_arg = request.args.get('page')
	if page_arg is not None:
		actual_page = int(page_arg)
	else:
		actual_page= 1
	off_set = (per_page*int(actual_page))-per_page
	if res_count > per_page and per_page > 0:
		pages= int(res_count / per_page)
		if res_count % per_page != 0:
			pages += 1
	else:
		pages = 1
	iter_pages=[]
	has_preview= False
	has_next= False
	next_page=0
	prev_page=0
	for i in range(pages):
		iter_pages.append(i+1)
	if actual_page > 1:
		has_preview= True
	else:
		has_preview= None
	if actual_page < pages:
		has_next= True
	else:
		has_next= None
	
	# showing progressively just a part of pages numbers
	index = actual_page
	max_index= int(pages)
	start_index= index - 3 if index >=3 else 0
	end_index = index + 3 if index <= max_index - 3 else max_index
	page_range = list(range(1,pages))[int(start_index):int(end_index)]
	pagination={
		"iter_pages":iter_pages,
		"page_range":page_range,
		"page":actual_page,
		"has_prev":has_preview,
		"has_next":has_next,
		"next_page":actual_page+1,
		"prev_page":actual_page-1,
		"total":pages,
	}
	return pagination
