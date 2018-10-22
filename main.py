from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'SecretKey@'

blogs =[]


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner, created=None):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return'<Title %r>' % self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password= db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def allowed_login():
    allowed_login = ['login', 'register', 'blog', 'index']
    if request.endpoint not in allowed_login and 'email' not in session:
        flash ('Must login in!')
        print(request.endpoint)
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash ('You are logged in')
            return redirect ('/newpost')
        else:
            flash('Password is incorrect, or User is not registered', 'error')

    return render_template('login.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify_password']
        if password != verify:
            flash("Passwords do not match")
        else:
            registered_user = User.query.filter_by(email = email).first()

        if not registered_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')
        else:
            flash ("User email already exist")

    return render_template('register.html')

app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/', methods=['GET'])
@app.route('/blog', methods=['POST'])
def index():
    post_id = request.args.get('id', "")
    if post_id == "":
        posts = Blog.query.order_by("Blog.id DESC").all()
        return render_template('blog_list.html', posts=posts)
    post = Blog.query.filter_by(id=post_id).first()
    return render_template('newpost.html', post=post, post_id=post_id)


@app.route("/newpost", methods=['POST'])
def add_newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(email=session['email']).first()

        if not title:
            flash('Please enter a title for your blog entry!')
            body = request.form['body']
            return redirect('/newpost')
        if not body:
            flash('Please add your entry into your blog!')
            title=request.form['title']
            return redirect('/newpost')

        newblog = Blog(title, body, owner)
        db.session.add(newblog)
        db.session.commit()
        blog_now = "./blog?id=" + str(newblog.id)

        return redirect(blog_now)

    return render_template('newpost.html')


#@app.route('/blog', methods=['POST', 'GET'])
#def index2():

#   if request.args:
#        id = request.args.get('id')
#        blog = Blog.query.get(id)
#        title = blog.title
#        body = blog.body
#        return render_template('onepost.html', title=title, body=body)
      
    
#    return render_template('blog.html', blogs=current_blog())


if __name__ == '__main__':
    app.run()