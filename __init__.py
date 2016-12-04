from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.sqlite3'
app.config['SECRET_KEY'] = "HiiiiiiiiiMdR"

db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column('article_id', db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
    source = db.Column(db.String(256))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __init__(self, title, content, category, author, source, date=None):
        self.title = title
        self.content = content
        if date is None:
            date = datetime.datetime.utcnow()
        self.date = date
        self.category_id = category
        self.author_id = author
        self.source = source


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    website = db.Column(db.String(256))
    picture = db.Column(db.String(256))
    articles = db.relationship('Article', backref='author', lazy='dynamic')

    def __init__(self, name, website, picture):
        self.name = name
        self.website = website
        self.picture = picture


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __init__(self, name):
        self.name = name


@app.route('/')
def show_all_articles():
    active=None
    articles = Article.query.all()
    categories = Category.query.all()
    return render_template("blog.html",articles=articles,categories=categories,active=active)


@app.route('/article/<key>')
def get_article(key):
    return render_template("blog.html",article=Article.query.get(key))


@app.route('/category/<key>')
def get_category(key):
    active = key
    categories = Category.query.all()
    articles = Article.query.filter_by(category_id=key).all()
    return render_template("blog.html",categories=categories,articles=articles,active=active)


@app.route('/newArticle', methods=["POST","GET"])
def create_article():
    if request.method == 'POST':
        if not request.form['title'] or not request.form['content'] or not request.form['category'] or not request.form['author']:
            flash('Please enter all the fields', 'error')
        else:
            if not request.form['source']:
                source = None
            else:
                source = request.form['source']
            article = Article(request.form['title'], request.form['content'], request.form['category'], request.form['author'], source)

            db.session.add(article)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all_articles'))
    return render_template('new_article.html',authors=Author.query.all(),categories=Category.query.all())


@app.route('/newAuthor', methods=["POST","GET"])
def create_author():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['website'] or not request.form['picture']:
            flash('Please enter all the fields', 'error')
        else:
            author = Author(request.form['name'], request.form['website'], request.form['picture'])
            db.session.add(author)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all_articles'))
    return render_template('new_author.html')


@app.route('/newCategory', methods=["POST","GET"])
def create_category():
    if request.method == 'POST':
        if not request.form['category']:
            flash('Please enter all the fields', 'error')
        else:
            category = Category(request.form['category'])
            db.session.add(category)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all_articles'))
    return render_template('new_category.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)