DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;
--
-- Create Table users
--
CREATE TABLE IF NOT EXISTS "users" (
	"id" serial NOT NULL PRIMARY KEY, 
	"username" varchar(100) NOT NULL, 
	"email" varchar(100) NOT NULL, 
	"passwd" varchar(100) NOT NULL, 
	"auth_level" integer NOT NULL);

--
-- Create Table books
--
CREATE TABLE IF NOT EXISTS "books" (
	"id" serial NOT NULL PRIMARY KEY, 
	"isbn" varchar(12) UNIQUE NOT NULL,
	"title" varchar(100) NOT NULL,
	"author" varchar(100) NOT NULL,
	"year" integer NOT NULL);

--
-- Create Table reviews
--
CREATE TABLE IF NOT EXISTS "reviews" (
	"id" serial NOT NULL PRIMARY KEY, 
	"isbn" varchar(12) NOT NULL REFERENCES books(isbn) ON DELETE CASCADE, 
	"user_id" integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	"heading" varchar(100) DEFAULT 'No heading',
	"comments" TEXT DEFAULT NULL,
	"rating" float NOT NULL);
