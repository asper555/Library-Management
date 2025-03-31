from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date, datetime
from decimal import Decimal
from models import db, Book, Customer, Borrowing, Transaction, BookLocation
from flask import jsonify
from sqlalchemy import cast, String, text, update


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://neondb_owner:npg_FauoX5vlHN7P@ep-restless-dream-a19z2lol-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', flag=0)

@app.route('/librarian_login')
def librarian_login():
    return render_template('librarian_login.html', flag=0)

@app.route('/test-db')
def test_db():
    try:
        db.session.execute(text("SELECT * FROM books"))
        return 'DB Connected Successfully!'
    except Exception as e:
        return f'Connection Failed: {e}'

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    books = []
    active_section = None
    borrow_details = []
    transactions = []
    
    if request.method == 'POST':
        # Handle search functionality
        search_terms = request.form.get('search_terms')
        action_type = request.form.get('action_type')
        customer_names = request.form.get('customer_names')
        customer_id = request.form.get('customer_id')
        
        # Book search
        if search_terms:
            active_section = 'searchbar'
            books = Book.query.filter(
                (Book.title.ilike(f"%{search_terms}%")) |
                (cast(Book.id, String).ilike(f"%{search_terms}%"))
            ).all()
        
        # Borrow details
        elif action_type == 'borrow_books':
            active_section = 'Borrowdetails'
            customer = Customer.query.get(customer_id)
            
            if customer:
                borrow_details = Borrowing.query.filter_by(customer_id=customer.id).all()
                if not borrow_details:
                    flash('No borrowing records found for this customer.', 'warning')
            else:
                flash('Customer not found.', 'danger')
        
        # Transaction details
        elif action_type == 'Transactions_details':
            active_section = 'transactions'
            customer = Customer.query.get(customer_id)
            
            if customer:
                transactions = Transaction.query.filter_by(customer_id=customer.id).all()
                if not transactions:
                    flash('No transaction records found for this customer.', 'warning')
            else:
                flash('Customer not found.', 'danger')
    
    return render_template('customer.html', 
                          books=books, 
                          borrow_details=borrow_details, 
                          transactions=transactions, 
                          active_section=active_section)



@app.route('/librarian_operations', methods=['GET', 'POST'])
def librarian_operations():
    flag = 0
    active_section = None
    customers=[]
    if request.method == 'POST':
        action = request.form.get('action_type')
        try:
            if action == 'add_book':
                active_section = 'AddBook'
                title = request.form['title']
                author = request.form['author']
                category = request.form.get('category')
                publisher = request.form.get('publisher')
                published_year = request.form.get('published_year')
                section = request.form.get('section')
                shelf = request.form.get('shelf')
                available_copies = request.form.get('available_copies')

                if Book.query.filter_by(title=title).first():
                    flash('Book already exists.', 'warning')
                else:
                    new_book = Book(
                        title=title,
                        author=author,
                        category=category,
                        publisher=publisher,
                        published_year=int(published_year) if published_year else None,
                        available_copies=int(available_copies) if available_copies else 1
                    )
                    db.session.add(new_book)
                    db.session.commit()
                    
                    new_location = BookLocation(
                        book_id=new_book.id,
                        section=section,
                        shelf=shelf
                    )
                    db.session.add(new_location)
                    db.session.commit()
                    flash('Book added successfully!', 'success')

            elif action == 'add_customer':
                active_section = 'AddCustomer'
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                new_customer = Customer(name=name, email=email, phone=phone, total_fine=0)
                db.session.add(new_customer)
                db.session.commit()
                flash('Customer added successfully!', 'success')

            elif action == 'borrow_book':
                active_section = 'BorrowBook'
                customer_id = request.form.get('customer_id')
                customer_name = request.form.get('customer_name')
                book_title = request.form.get('book_title')
                return_date = request.form.get('return_date')

                customer = Customer.query.get(customer_id)
                book = Book.query.filter_by(title=book_title).first()

                if not customer:
                    flash('Customer not found.', 'danger')
                elif not book:
                    flash('Book not found.', 'danger')
                elif book.available_copies <= 0:
                    flash('No copies available to borrow.', 'warning')
                else:
                    # Create borrowing record
                    borrowing = Borrowing(
                        customer_id=customer.id,
                        book_id=book.id,
                        book_title=book.title,
                        borrow_date=date.today(),
                        return_date=return_date,
                        status='Borrowed'
                    )
                    db.session.add(borrowing)
                    
                    # Decrement available copies directly in the database
                    stmt = update(Book).where(Book.id == book.id).values(available_copies=Book.available_copies - 1)
                    db.session.execute(stmt)
                    
                    db.session.commit()
                    flash('Book borrowed successfully!', 'success')

            elif action == 'return_book':
                active_section = 'ReturnBook'
                book_title = request.form.get('book_title')
                customer_id = request.form.get('customer_id')
                customer_name = request.form.get('customer_name')

                book = Book.query.filter_by(title=book_title).first()
                customer = Customer.query.get(customer_id)
                
                if book and customer:
                    borrowing = Borrowing.query.filter_by(book_id=book.id, customer_id=customer.id, status='Borrowed').first()
                    if borrowing:
                        # Update borrowing record
                        borrowing.status = 'Returned'
                        borrowing.return_date = date.today()
                        
                        # Increment available copies directly in the database
                        stmt = update(Book).where(Book.id == book.id).values(available_copies=Book.available_copies + 1)
                        db.session.execute(stmt)
                        
                        db.session.commit()
                        flash('Book returned successfully!', 'success')
                    else:
                        flash('No active borrowing record found for this book and customer.', 'danger')
                else:
                    flash('Book or Customer not found.', 'danger')

            elif action == 'add_fine':
                active_section = 'AddFine'
                customer_id = request.form.get('customer_id')
                customer_name = request.form.get('customer_name')
                fine_amount = request.form.get('fine_amount')

                customer = Customer.query.get(customer_id)
                if customer:
                    new_transaction = Transaction(
                        customer_id=customer.id,
                        transaction_type="Adding Fine",
                        amount=fine_amount,
                        transaction_date=date.today()
                    )
                    db.session.add(new_transaction)
                    
                    # Update customer's total fine directly in the database
                    stmt = update(Customer).where(Customer.id == customer.id).values(
                        total_fine=Customer.total_fine + Decimal(fine_amount)
                    )
                    db.session.execute(stmt)
                    
                    db.session.commit()
                    flash(f'Fine of {fine_amount} added to {customer_name}.', 'success')
                else:
                    flash('Customer not found.', 'danger')

            elif action == 'pay_fine':
                active_section = 'PayFine'
                customer_id = int(request.form.get('customer_id'))
                customer_name = request.form.get('customer_name')
                fine_amount = request.form.get('pay_amount')

                customer = Customer.query.get(customer_id)
                
                if customer:
                    if Decimal(fine_amount) <= customer.total_fine:
                        new_transaction = Transaction(
                            customer_id=customer.id,
                            transaction_type="Paying Fine",
                            amount=fine_amount,
                            transaction_date=date.today()
                        )
                        db.session.add(new_transaction)
                        
                        # Update customer's total fine directly in the database
                        stmt = update(Customer).where(Customer.id == customer.id).values(
                            total_fine=Customer.total_fine - Decimal(fine_amount)
                        )
                        db.session.execute(stmt)
                        
                        db.session.commit()
                        flash(f'{fine_amount} fine paid by {customer_name}.', 'success')
                    else:
                        flash('Fine amount exceeds the total fine.', 'warning')
                else:
                    flash('Customer not found.', 'danger')

            elif action == 'search_customer':
                active_section = 'SearchCustomer'
                customer_name = request.form.get('customer_name')
                customer_id = int(request.form.get('customer_id'))
                customers = Customer.query.get(customer_id)
                
                flag = 1  

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'danger')

    return render_template('librarian_operations.html', 
                          customers=customers, 
                          flag=flag, 
                          active_section=active_section) 

if __name__ == '__main__':
    app.run(debug=True)