from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


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


    def __init__(self, title, body, owner, created=None):
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


@app.before_request
def allowed_login():

    allowed_login = ['login', 'register', 'blog', 'blogpage']

    if request.endpoint not in allowed_login and 'email' not in session:
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
            flash ('You are logged in')
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

        user_error =""
        pass_error=""
        pass_verify=""
        space =''

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            user_error = 'Email already in system'
            password = ''
            verify = ''

        if len(email) <3 or len(email)>30 or email.count(space) !=0:
            user_error = 'Please enter a valid email address'
            password = ''
            verify = ''

        if len(password) <3 or len(password)>20 or password.count(space) !=0:
            pass_error ='Please enter a valid password between 3-20 characters, no spaces'
            password = ''
            verify = ''

        if verify != password:
            pass_verify = 'Passwords do not match'
            password = ''
            verify = ''
        
        if not user_error and not pass_error and not pass_verify:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash ('Your account has been created!','info')
            return redirect('/newpost')

        else:
            flash("Account not created! Please see below error message.",'error')
            return render_template('register.html', email=email, user_error=user_error,
            password=password, pass_error=pass_error, verify=verify, pass_verify=pass_verify)
        
    return render_template('register.html')


@app.route('/blog', methods=['POST', 'GET'])
def entry():
    
    if 'id' in request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id)
        return render_template('onepost.html', blogs=blogs)

    elif 'user' in request.args:
        author = request.args.get('email')
        user = User.query.filter_by(email=author).first()
        blogs = user.blogs
        return render_template('mainpage.html', author=author, user=user, blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


app.route('/logout')
def logout():
    del session['email']
    flash('Your session has been ended and you are logged out!', 'info')
    return redirect('/blog')


@app.route("/newpost", methods=['POST', 'GET'])
def add_newpost():

    if request.method == 'POST':
        owner = User.query.filter_by(email=session['email']).first()
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash('Please enter a title for your blog entry!','error')
            body = request.form['body']
            return redirect('/newpost')
        if not body:
            flash('Please add your entry into your blog!','error')
            title=request.form['title']
            return redirect('/newpost')

        newblog = Blog(title, body, owner)
        db.session.add(newblog)
        db.session.commit()
        blog_now = "./blog?id=" + str(newblog.id)

        return redirect(blog_now)

    return render_template('newpost.html')


@app.route('/blog', methods=['POST', 'GET'])
def index():
    users=User.query.all()
    return render_template('blogpage.html', users=users)


if __name__ == '__main__':
    app.run() 