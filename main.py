from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'jjert%**lle'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120)) 

    def __init__(self,title,body):
        self.title = title
        self.body = body

    def valid(self):
        if self.title and self.body:
            return True
        else:
            return False

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    entry = Blog.query.all()
    id = request.query_string
    if request.method == 'GET':
        if not id:
            return render_template('blog.html', entry=entry)
        else:
            new_entry = int(request.args.get('new_entry'))
            entries = Blog.query.get(new_entry)
            return render_template('new_entry_post.html', entries=entries)


@app.route('/new_entry', methods=['POST', 'GET'])
def new_blog_entry():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
           flash('Please enter a title for your blog entry!')
           return redirect('/new_entry')
        if not body:
            flash('Please add your entry into your blog!')
            return redirect('/new_entry')
        
        else:
            new_entry = Blog(title, body)
            db.session.add(new_entry)
            db.session.comit()

            new_id = new_entry.id
            blog = Blog.query.get(new_id)
            return render_template('new_entry_post.html', blog=blog)

        return redirect('/blog')

    return render_template('new_entry_post.html')
if __name__ == '__main__':
    app.run()