# from flask_sqlalchemy import SQLAlchemy
# from datetime import date

# db = SQLAlchemy()

# class Book(db.Model):
#     __tablename__ = 'books'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     author = db.Column(db.String(100), nullable=False)
#     category = db.Column(db.String(50))
#     publisher = db.Column(db.String(100))
#     published_year = db.Column(db.Integer)
#     available_copies = db.Column(db.Integer, default=1)
#     section = db.Column(db.String(20))
#     shelf = db.Column(db.String(20))
#     borrowings = db.relationship('Borrowing', backref='book', lazy=True)

# class Customer(db.Model):
#     __tablename__ = 'customers'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     email = db.Column(db.String(255), nullable=False)
#     phone = db.Column(db.String(15), nullable=False)
#     total_fine = db.Column(db.Numeric(10, 2), default=0, nullable=False)
#     borrowings = db.relationship('Borrowing', backref='customer', lazy=True)
#     transactions = db.relationship('Transaction', backref='customer', lazy=True)

# class Borrowing(db.Model):
#     __tablename__ = 'borrowings'
#     id = db.Column(db.Integer, primary_key=True)
#     book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
#     customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
#     book_title = db.Column(db.String(255), nullable=False)
#     borrow_date = db.Column(db.Date, nullable=False, default=date.today)
#     return_date = db.Column(db.Date)
#     status = db.Column(db.String(50), default="Borrowed")

# class Transaction(db.Model):
#     __tablename__ = 'transactions'
#     id = db.Column(db.Integer, primary_key=True)
#     customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
#     transaction_type = db.Column(db.String(20))  # "Fine Added" or "Fine Paid"
#     amount = db.Column(db.Numeric(10, 2))
#     transaction_date = db.Column(db.Date, default=date.today)


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    publisher = db.Column(db.String(100))
    published_year = db.Column(db.Integer)
    available_copies = db.Column(db.Integer, default=1)

    # Establish relationship with BookLocation (One-to-One)
    location = relationship('BookLocation', uselist=False, backref='book', lazy="joined")

    # Hybrid properties to access section and shelf directly
    @hybrid_property
    def section(self):
        return self.location.section if self.location else None

    @hybrid_property
    def shelf(self):
        return self.location.shelf if self.location else None

    borrowings = relationship('Borrowing', backref='book', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    total_fine = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    borrowings = relationship('Borrowing', backref='customer', lazy=True)
    transactions = relationship('Transaction', backref='customer', lazy=True)

class Borrowing(db.Model):
    __tablename__ = 'borrowings'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_title = db.Column(db.String(255), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False, default=date.today)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Borrowed")

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    transaction_type = db.Column(db.String(20))  # "Fine Added" or "Fine Paid"
    amount = db.Column(db.Numeric(10, 2))
    transaction_date = db.Column(db.Date, default=date.today)

class BookLocation(db.Model):
    __tablename__ = 'book_locations'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    section = db.Column(db.String(50), nullable=False)
    shelf = db.Column(db.String(10), nullable=False)
