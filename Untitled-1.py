from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import re



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['POST_ON_PAGE'] = 5
app.secret_key = 'SecretKey@'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash= db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)



@app.route('/newpost', methods=['POST','GET'])
def user_logged_in():

    title = request.form['title']
    body = request.form['body']
    owner = User.query.filter_by(email=session['email']).first()

    if request.method =='POST':
        title = request.form['title']
        body = request.form['body']
        posts = Blog(title, body, owner)
        db.session.add(posts)
        db.session.commit()

    if not title:
        flash('Please enter a title for your blog entry!','error')
        body = request.form['body']
        return redirect('/newpost')
    if not body:
        flash('Please add your entry into your blog!','error')
        title=request.form['title']
        return redirect('/newpost')
    else:
        return render_template('onepost.html', title=title, body=body, user_id=owner, posts=posts)

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    post_id = request.args.get('id', '')
    user_id = request.args.get('user', '')

    if post_id != '':
        post = Blog.query.filter_by(id=post_id).first()
        return render_template('onepost.html', post=post)

    if user_id != '':
        posts= Blog.query.filter_by(owner_id=user_id).order_by('Blog.id DESC')
        author = User.query.get(user_id).email
        return render_template('mainpage.html', author=author, posts=posts)

    posts = Blog.query.order_by("Blog.id DESC")
    return render_template ('mainpage.html', post_for = 'All Users', posts=posts)   
    


@app.before_request
def allowed_routes():

    allowed_routes= ['login', 'register', 'blog', 'index']

    if request.endpoint not in allowed_routes and 'email' not in session:
        flash ('Must login in!')
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()


        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash ('Welcome' + email + 'are logged in', 'information')
            print(session)
            return redirect ('/newpost')

        if not user:
            flash(' User is not registered', 'error')
            return render_template('login.html')
        else:
            flash('Password is incorrect', 'error')
            return render_template('login.html', email=email)

    return render_template('login.html')


@app.route('/register', methods=["POST", "GET"])
def register():


    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify_password']

        if email == '' or password == '' or verify == '':
            flash('One or more boxes are invalid', 'error')
            return redirect('/register')

        elif len(email) < 3:
            flash('Username invalid', 'error')
            return redirect('/register')

        elif len(password) < 3 or len(verify) < 3:
            flash('Password is invalid', 'error')
            return redirect('/register')

        elif password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/register')


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash('Welcome' + email + 'your account has been created!','information')
            return redirect('/newpost')

        else:
            flash("Username already exists",'error')
            return redirect('/register')
        
    return render_template('register.html')


@app.route('/logout')
def logout():
    del session['email']
    flash('Your session has been ended and you are logged out!', 'information')
    return redirect('/blog')


@app.route("/mainpage")
def index():

    page = request.args.get('page', 1, type=int)
    paginate = User.query.paginate(page, 5, False)
    return render_template('index.html', authors=paginate.items )


if __name__ == '__main__':
    app.run() 