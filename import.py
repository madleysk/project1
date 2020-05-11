import csv
import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

conn = psycopg2.connect(engine, sslmode='require')

def main():
	# Creating tables structure if not exists
	with open('db_sql.sql') as fichier:
		lignes = fichier.read().split(';')
		for ligne in lignes:
			if len(ligne)<10:
				conn.execute(ligne)
				conn.commit()
		conn.commit()
	# inserting books
	line_count = 0
	with open("books.csv") as f:
		reader = csv.reader(f)
		for isbn, title, author, year  in reader:
			if line_count > 0:
				conn.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
						   {"isbn": isbn, "title": title, "author": author, "year": year})
				#print(f"Added book {title} from {author} appeared in {year}.")
			line_count += 1
		conn.commit()
	print(f"{line_count-1} books imported !")

"""
import csv

def main():
	print('importing books...')
	lines = import_books('books.csv')
	print(f"{lines} lines imported !")

def import_books(filename):
	with open(filename) as csv_file:
		csv_reader = csv.reader(csv_file,delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count +=1
			else:
				new_book = Book(row[0],row[1],row[2],row[3])
				db.session.add(new_book)
				line_count +=1
		db.commit()
	return line_count-1
"""				

if __name__=='__main__':
	main()
