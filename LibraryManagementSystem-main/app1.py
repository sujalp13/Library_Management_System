from flask import Flask
from flask_mysqldb import MySQL
from datetime import datetime
from flask import render_template, request, redirect, url_for, json, jsonify, flash, session
from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField ,validators, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash
app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jyotishna@1'
app.config['MYSQL_DB'] = 'lib'

mysql = MySQL(app)
# con=mysql.connection()
# cur = con.cursor()
class RegisterForm(Form):
    name=StringField("Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    rollNo=StringField("Roll No", validators=[validators.Length(min=10, max=25), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])
    submit = SubmitField('Submit')

class LoginForm(Form):
    loginId = StringField("Email/Roll No", validators=[validators.Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])
    submit = SubmitField('Submit')

class libRegisterForm(Form):
    name=StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])
    submit = SubmitField('Submit')

class SearchForm(Form):
    getall=BooleanField("See all books")
    book= StringField("Book_Title OR Author")
    submit = SubmitField('Submit')

class ReviewForm(Form):
    rating=IntegerField("1-5", validators=[validators.Length(min=1, max=5)])
    Review= TextAreaField("Review")
    submit = SubmitField('Submit')

class addbook(Form):
    isbn_no=IntegerField("isbn_no", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    title=StringField("title", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    author=StringField("author", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    genre=StringField("genre", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    yop=IntegerField("publication year", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    copy_no=IntegerField("Copy", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    submit = SubmitField('Submit')

class delete(Form):
    isbn_no=IntegerField("isbn_no", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    copy_no=IntegerField("Copy", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    submit = SubmitField('Submit')
  
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        form = RegisterForm(request.form)
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        name=form.name.data
        roll = form.rollNo.data
        con=mysql.connection
        cur = con.cursor()
        cur.execute("INSERT INTO user(name, user_id, password) VALUES (%s, %s, %s)", (name,roll,hashed_password,))
        con.commit()
        cur.close()
        flash('Thank You for registering')
        return redirect(url_for('login'))
    form=RegisterForm()
    return render_template('index.html',form=form)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=="POST":
        form=LoginForm(request.form)
        loginId = form.loginId.data
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        con=mysql.connection
        cur = con.cursor()
        cur.execute("Select user_id, password from user where user_id=%s",(loginId,))
        con.commit()
        user=cur.fetchone()
        cur.close()
        if user:
            if check_password_hash(user[1], form.password.data):
                session['logged_in']=True
                session['user_id']=user[0]
                print('1')
                return redirect(url_for('home'))
        else:
            flash('Username or Password Incorrect', "Danger")
            return redirect(url_for('login'))
    form=LoginForm()
    return render_template('login.html',form=form)

@app.route('/home/', methods=['GET'])
def home():
    roll=None
    data=None
    if not session.get('logged_in') is None and session['logged_in']:
        roll=session['user_id']
        con=mysql.connection
        cur = con.cursor()
        cur.execute("select isbn_no, title, author, genre from books where genre in(select genre from books where isbn_no in(select isbn_no from reviews where rating>2 and user_id=%s))", (roll,))
        con.commit()
        data=cur.fetchall()
        cur.close()
    form=SearchForm()
    return render_template('home.html', user=roll, form=form, data=data)

@app.route('/home/search', methods=['GET', 'POST'])
def search():
    form=SearchForm(request.form)
    if request.method == "POST":
        allbook=form.getall.data
        if allbook:
            con=mysql.connection
            cur = con.cursor()
            cur.execute("SELECT isbn_no, title, author from books")
            con.commit()
            data=cur.fetchall()
            cur.close()
        else:
            book=form.book.data
            # search by author or book
            con=mysql.connection
            cur = con.cursor()
            cur.execute("SELECT isbn_no, title, author from books WHERE title LIKE %s OR author LIKE %s", (book, book,))
            con.commit()
            data=cur.fetchall()
            cur.close()
        # all in the search box will return all the tuples
        if data:
            return render_template('search.html', data=data)
    return redirect(url_for('home'))
    
@app.route('/home/<isbn>', methods=['GET', 'POST'])
def book_detail(isbn):
    con=mysql.connection
    cur = con.cursor()
    cur.execute("SELECT * FROM books where isbn_no=%s", (int(isbn),))
    con.commit()
    data=cur.fetchone()
    cur.close()
    con=mysql.connection
    cur=con.cursor()
    cur.execute("SELECT user.name, reviews.rating, reviews.review FROM user, reviews where isbn_no=%s AND user.user_id=reviews.user_id", (int(isbn),))
    con.commit()
    data1=cur.fetchall()
    cur.close()
    form=ReviewForm()
    return render_template('book_detail.html', data=data, data1=data1, form=form)

@app.route('/home/like/<isbn>', methods=['GET', 'POST'])
def like(isbn):
    if not session.get('logged_in'):
        flash('Login to continue')
        return redirect(url_for('login'))
    con=mysql.connection
    cur = con.cursor()
    cur.execute("INSERT IGNORE INTO liked(user_id, isbn_no) values(%s, %s)",(session['user_id'], int(isbn),))
    con.commit()
    cur.close()
    return redirect(url_for('book_detail', isbn=isbn))
@app.route('/home/review/<isbn>', methods=['GET', 'POST'])
def add_review(isbn):
    if not session.get('logged_in'):
        flash('Login to continue')
        return redirect(url_for('login'))
    form=ReviewForm(request.form)
    if request.method == "POST":
        rat=form.rating.data
        review=None
        if form.Review.data:
            review=form.Review.data
        con=mysql.connection
        cur = con.cursor()
        cur.execute("REPLACE INTO reviews (user_id, isbn_no, rating, review) values(%s, %s, %s, %s)",(session['user_id'], int(isbn),int(rat), review,))
        con.commit()
        cur.close()
    return redirect(url_for('book_detail', isbn=isbn))

@app.route('/liblogin/', methods=['GET', 'POST'])
def liblogin():
    if request.method=="POST":
        form=LoginForm(request.form)
        email=form.loginId.data
        con=mysql.connection
        cur = con.cursor()
        cur.execute("Select lib_id, password from librarian where email=%s",(email,))
        con.commit()
        lib=cur.fetchone()
        cur.close()
        if lib:
            if check_password_hash(lib[1], form.password.data):
                session['logged_in']=True
                session['username']=lib[0]
                session['email'] = email
                session['account_type'] == 'lib'
                return redirect(url_for('libhome'))
        else:
            flash('Username or Password Incorrect', "Danger")
            return redirect(url_for('liblogin'))
    form=LoginForm()
    return render_template('liblogin.html',form=form)

@app.route('/libhome/', methods=['GET', 'POST'])
def libhome():
    return render_template('libhome.html')

@app.route('/addbooks/',methods=['GET', 'POST'])
def addbook1():
    if request.method=="POST":
        form=addbook(request.form)
        print(form)
        isbn_no=form.isbn_no.data
        title=form.title.data
        author=form.author.data
        yop=form.yop.data
        genre=form.genre.data
        copy_no=form.copy_no.data
        con=mysql.connection
        cur=con.cursor()
        cur.execute("INSERT INTO books(isbn_no, title, author, year_of_publication, genre) values(%s,%s,%s,%s,%s)",(int(isbn_no), title, author, int(yop), genre,))
        con.commit()
        status='on_shelf'
        cur.execute("INSERT INTO book_copies(isbn_no, copy_no) values(%s,%s)",(int(isbn_no),int(copy_no),))
        con.commit()
        flash('books been inserted')
        return redirect(url_for('libhome'))
    form=addbook()
    return render_template('addbook.html',form=form)


@app.route('/deletebooks/',methods=['GET', 'POST'])
def deletebook():
    if request.method=="POST":
        form=delete(request.form)
        isbn_no=form.isbn_no.data
        copy_no=form.copy_no.data
        con=mysql.connection
        cur=con.cursor()
        cur.execute("DELETE from book_copies where isbn_no=%s and copy_no=%s",(int(isbn_no), int(copy_no),))
        con.commit()
        cur.execute("UPDATE shelf set capacity=capacity+1 where shelf_id=%s",(int(shelf_id),))
        con.commit()
        cur.close()
        flash('book have been deleted')
        return redirect(url_for('libhome'))
    form=delete()
    return render_template('deletebook.html',form=form)

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
