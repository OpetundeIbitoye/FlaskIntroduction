from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.content}>"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    store_name = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Product {self.name}>"
    

@app.route('/landing')
def landing():
    return render_template('landing.html')  # Render the landing page

@app.route('/task-master')
def task_master():
    return redirect('/')  # Redirect to the Task Master project (your current index route)

@app.route('/assignment/', methods=['POST', 'GET'])
def assignment_index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('assignment/index.html', tasks=tasks)


@app.route('/assignment/delete/<int:id>')
def assignment_delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment/')
    except:
        return 'There was a problem deleting that task'


@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def assignment_update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('assignment/update.html', task=task)

from datetime import datetime

@app.route('/inventory')
def inventory():
    sort_by = request.args.get('sort_by', 'expiry_date')  # Default sorting by expiry_date
    selected_category = request.args.get('category', '')  # Get the selected category from the query params

    # Filter products based on the selected category
    if selected_category:
        products = Product.query.filter_by(category=selected_category).order_by(getattr(Product, sort_by)).all()
    else:
        products = Product.query.order_by(getattr(Product, sort_by)).all()

    # Get unique categories for the filter dropdown
    categories = Product.query.with_entities(Product.category).distinct().all()

    # Render the template with products and categories
    return render_template('inventory.html', products=products, categories=categories, datetime=datetime)

import base64
import os

# Define the folder to save uploaded images
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/inventory/add', methods=['POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        store_name = request.form['store_name']

        # Handle image upload
        image = request.files['image']
        image_path = None
        if image and allowed_file(image.filename):
            filename = image.filename
            image_path = os.path.join('uploads', filename)  # Only store relative path
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        # Create a new product object
        new_product = Product(
            name=name,
            category=category,
            quantity=quantity,
            price=price,
            expiry_date=expiry_date,
            store_name=store_name,
            image_path=image_path
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/inventory')
        except Exception as e:
            return f"There was an issue adding the product: {e}"

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') 
import io
import base64

# @app.route('/inventory/chart')
# def inventory_chart():
#     products = Product.query.all()
#     categories = [product.category for product in products]
#     category_counts = {category: categories.count(category) for category in set(categories)}

#     # Create the chart
#     fig, ax = plt.subplots()
#     ax.bar(category_counts.keys(), category_counts.values())
#     ax.set_title('Product Categories')
#     ax.set_xlabel('Categories')
#     ax.set_ylabel('Count')

#     # Save chart to a BytesIO stream
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     chart_url = base64.b64encode(img.getvalue()).decode()
#     plt.close()

#     return render_template('inventory_chart.html', chart_url=chart_url)

# @app.route('/inventory/chart')
# def inventory_chart():
#     products = Product.query.all()
#     categories = [product.category for product in products]
#     category_counts = {category: categories.count(category) for category in set(categories)}

#     # Create the chart
#     fig, ax = plt.subplots()
#     ax.bar(category_counts.keys(), category_counts.values())
#     ax.set_title('Product Categories')
#     ax.set_xlabel('Categories')
#     ax.set_ylabel('Count')

#     # Save chart to a BytesIO stream
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     chart_url = base64.b64encode(img.getvalue()).decode()
#     plt.close()

#     return render_template('inventory_chart.html', chart_url=chart_url)


@app.route('/inventory/chart')
def inventory_chart():
    products = Product.query.all()
    
    # Chart for product categories
    categories = [product.category for product in products]
    category_counts = {category: categories.count(category) for category in set(categories)}
    fig, ax = plt.subplots()
    ax.bar(category_counts.keys(), category_counts.values(), color="blue")  # Consistent blue color
    ax.set_title('Product Categories')
    ax.set_xlabel('Categories')
    ax.set_ylabel('Count')
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    chart_url_1 = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    return render_template(
        'inventory_chart.html',
        chart_url_1=chart_url_1
    )



@app.route('/inventory/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.category = request.form['category']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])
        product.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        product.store_name = request.form['store_name']
        
        # Handle image update
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = image.filename
                image_path = os.path.join('uploads', filename)  # Only store relative path
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save in static/uploads
                product.image_path = image_path

        try:
            db.session.commit()
            return redirect('/inventory')
        except Exception as e:
            return f"There was an issue updating the product: {e}"
    else:
        return render_template('update_product.html', product=product)

@app.route('/inventory/delete/<int:id>', methods=['GET'])
def delete_product(id):
    product = Product.query.get_or_404(id)

    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/inventory')
    except Exception as e:
        return f"There was an issue deleting the product: {e}"

@app.route('/inventory/download_csv')
def download_inventory_csv():
    products = Product.query.all()
    response = make_response()
    response.headers['Content-Disposition'] = 'attachment; filename=inventory.csv'
    response.headers['Content-Type'] = 'text/csv'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Quantity', 'Price', 'Expiry Date', 'Store Name'])
    for product in products:
        writer.writerow([
            product.name,
            product.category,
            product.quantity,
            product.price,
            product.expiry_date.strftime('%Y-%m-%d'),
            product.store_name
        ])

    return response




if __name__ == "__main__":
    app.run(debug=True)
