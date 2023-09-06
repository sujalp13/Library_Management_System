CREATE TABLE user(
user_id VARCHAR(10) NOT NULL UNIQUE,
name VARCHAR(50) NOT NULL,
password Varchar(500) NOT NULL,
PRIMARY KEY(user_id));

CREATE TABLE librarian(
name VARCHAR(45),
email VARCHAR(70) NOT NULL,
password VARCHAR(30) NOT NULL,
lib_id INT NOT NULL AUTO_INCREMENT,
PRIMARY KEY(lib_id));

CREATE TABLE books(
isbn_no VARCHAR(45) NOT NULL,
title VARCHAR(100) NOT NULL,
author VARCHAR(100) NOT NULL,
year_of_publication INT NOT NULL,
genre VARCHAR(100) NOT NULL,
PRIMARY KEY(isbn_no));


CREATE TABLE book_copies(
isbn_no VARCHAR(45) NOT NULL,
copy_no INT NOT NULL,
current_status boolean not null default 0,
user_id VARCHAR(10),
issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
due_date DATETIME generated always as (issued_date + interval 1 month),
PRIMARY KEY(isbn_no, copy_no),
FOREIGN KEY (user_id) REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (isbn_no) REFERENCES books(isbn_no) ON UPDATE CASCADE ON DELETE CASCADE);

CREATE TABLE liked(
user_id VARCHAR(10) NOT NULL,
isbn_no VARCHAR(45) NOT NULL,
PRIMARY KEY(user_id,isbn_no),
FOREIGN KEY (user_id) REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (isbn_no) REFERENCES books(isbn_no) ON UPDATE CASCADE ON DELETE CASCADE);

CREATE table reviews(
user_id VARCHAR(10) NOT NULL,
isbn_no VARCHAR(45) NOT NULL,
review VARCHAR(100),
rating INT NOT NULL,
PRIMARY KEY(user_id,isbn_no),
FOREIGN KEY (user_id) REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (isbn_no) REFERENCES books(isbn_no) ON UPDATE CASCADE ON DELETE CASCADE);
