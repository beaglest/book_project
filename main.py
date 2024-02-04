from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import Integer, String, Float, event
from sqlalchemy import create_engine, select
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)
my_session = Session()


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable="NOT NULL", unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable="NOT NULL")
    rating: Mapped[float] = mapped_column(Float, nullable="NOT NULL")


with app.app_context():
    db.create_all()



@app.route('/')
def home():
    with app.app_context():
        all_books = Book.query.all()

    return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():

    if request.method == 'POST':

        new_book = Book(title=request.form['title'], author=request.form['author'],
                        rating=float(request.form['rating']))
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template('add.html')


@app.route("/edit/<sid>", methods=['GET', 'POST'])
def edit(sid):

    if request.method == 'POST':
        book_id = sid
        with app.app_context():
            book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
            # or book_to_update = db.get_or_404(Book, book_id)
            book_to_update.rating = float(request.form['nrating'])
            db.session.commit()
        return redirect(url_for("home"))

    else:

        edit_book = Book.query.filter_by(id=sid).all()
        return render_template('edit.html', book=edit_book)


@app.route("/delete/<sid>", methods=['GET', 'POST'])
def delete(sid):

    book_id = sid
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
