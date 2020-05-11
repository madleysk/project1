--
-- Create Table users
--
CREATE TABLE IF NOT EXISTS "users" (
	"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
	"username" varchar(100) NOT NULL, 
	"email" varchar(100) NOT NULL, 
	"passwd" varchar(100) NOT NULL, 
	"auth_level" integer NOT NULL);

--
-- Create Table books
--
CREATE TABLE IF NOT EXISTS "books" (
	"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
	"isbn" varchar(12) NOT NULL,
	"title" varchar(100) NOT NULL,
	"author" varchar(100) NOT NULL,
	"year" integer NOT NULL);

--
-- Create Table reviews
--
CREATE TABLE IF NOT EXISTS "reviews" (
	"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
	"isbn" varchar(12) NOT NULL REFERENCES books(isbn), 
	"user_id" integer NOT NULL REFERENCES users(id),
	"heading" varchar(100) DEFAULT 'No heading',
	"comments" TEXT DEFAULT NULL,
	"rating" float NOT NULL);
