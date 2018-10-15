from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'SecretKey@'

blogs =[]


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2500))
    

    def __init__(self,title,body):
        self.title = title
        self.body = body
      

    def __repr__(self):
        return'<Title %r>' % self.title


def current_blog():
    return Blog.query.all()


@app.route("/newpost", methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        

        if not title:
            flash('Please enter a title for your blog entry!')
            return redirect('/newpost')
        if not body:
            flash('Please add your entry into your blog!')
            return redirect('/newpost')

        newblog = Blog(title, body)
        db.session.add(newblog)
        db.session.commit()
        blog_now = "./blog?id=" + str(newblog.id)

        return redirect(blog_now)

    return render_template('newpost.html')


@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.args:
        id = request.args.get('id')
        blog = Blog.query.get(id)
        title = blog.title
        body = blog.body
        return render_template('onepost.html', title=title, body=body)
      
    
    return render_template('blog.html', blogs=current_blog())


if __name__ == '__main__':
    app.run()