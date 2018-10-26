from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'SecretKey@'


db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date_written = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user
    def __repr__(self):
        return self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    pw_hash= db.Column(db.String(120), nullable=False)
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, name, password):
        self.name = name
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return self.name


@app.before_request
def allowed_login():

    allowed_login = ['login', 'index', 'blog', 'register', 'static']

    if request.endpoint not in allowed_login and not session:
        flash ('Must login in!', 'error')
        return redirect('/login')


@app.route('/')
def index():

    users = User.query.all()
    return render_template('index.html', users=users)



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()

        if user and check_pw_hash(password, user.pw_hash):
            session['name'] = name
            flash ('You are logged in', 'information')
            return redirect ('/newpost')

        if not user:
            flash(' User is not registered', 'error')
            return render_template('login.html')
        else:
            flash('Password is incorrect', 'error')
            return render_template('login.html', name=name)

    return render_template('login.html')


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        verify = request.form['verify_password']

        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            flash('Username already in the system', 'error')
            return redirect('/login')

        elif len(name) <3 or len(name)>30:
            flash('Username must be between 3 and 20 characters', 'error')
            return redirect('/register')

        elif len(password) <3 or len(password)>20:
            flash('Please enter a valid password between 3-20 characters, no spaces', 'error')

        elif verify != password:
             flash('Passwords do not match', 'error')
        
        elif not existing_user:
            new_user = User(name, password)
            db.session.add(new_user)
            db.session.commit()
            session['name'] = name
            flash('Your account has been created!','information')
            return redirect('/newpost')

    return render_template('register.html')


@app.route('/blog')
def blog():
   
    blogs = Blog.query.order_by('date_written DESC').all()
    return render_template('blog.html', blogs=blogs)


@app.route('/logout')
def logout():

   del session['name']
   flash('Your session has been ended and you are logged out!', 'information')
   return redirect('/')


@app.route("/newpost", methods=['POST', 'GET'])
def add_newpost():

    if not session:
        flash('User not logged in', 'error')
        return redirect('/login')

    if request.method == 'POST':
        owner = User.query.filter_by(name=session['name']).first()
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash('Please enter a title for your blog entry!','error')
            return render_template('/newpost', body=body)
        if not body:
            flash('Please add your entry into your blog!','error')
            return render_template('/newpost', title=title)

        newblog = Blog(title, body, owner)
        db.session.add(newblog)
        db.session.commit()

        blog_num = newblog.id
        return redirect('onepost?id={0}&user={1}'.format(blog_num, owner))

    return render_template('newpost.html')

@app.route('/onepost', methods=['POST', 'GET'])
def onepost():

    num = request.args.get('id')
    user = request.args.get('user')
    blog = Blog.query.filter_by(id=num).first()

    return render_template('onepost.html', blog=blog)

@app.route('/singleuser')
def singleuser():

    id = request.args.get('id')
    user_posts = Blog.query.filter_by(user_id=id).all()
    user = User.query.filter_by(id=id).first()
    return render_template('singleuser.html', user_posts=user_posts, user=user)

    

if __name__ == '__main__':
   app.run()