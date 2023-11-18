from api_application import api,app, db, roles_accepted, auth_required
from api_application.models import *
from flask_restful import Resource, reqparse, output_json, reqparse, fields, marshal_with
from flask import Blueprint, jsonify, request

category_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_on': fields.DateTime(dt_format='iso8601'),
    'no_of_products': fields.Integer
}

product_fields = {
    'id': fields.Integer,
    'category_id': fields.Integer,
    'name': fields.String,
    'manufacturer': fields.String,
    'expiry': fields.DateTime(dt_format='iso8601'),
    'rate_per_unit': fields.Float,
    'available_quantity': fields.Integer,
    'units': fields.String,
    'date_added': fields.DateTime(dt_format='iso8601')
}

class CategoryResource(Resource):
    @auth_required('token','session')
    @roles_accepted('admin')
    def get(self, category_id):
        category = Category.query.get(category_id)
        if category == None:
            return {'message': f'Category_id {category_id} is not in the database'}, 404
        else:
            return {
                'id': category.id,
                'name': category.name,
                'created_on': str(category.created_on),
                'no_of_products': category.no_of_products
            }, 200
    
    @auth_required('token', 'session')
    @roles_accepted('admin')
    def delete(self, category_id):
        category = Category.query.get(category_id)
        if category == None:
            return {'message': f'Category_id {category_id} is not in the database'}, 404
        for product in category.products:
            db.session.delete(product)
        db.session.delete(category)
        db.session.commit()
        return {'message': 'Category deleted'},200  
    
    @auth_required('token', 'session')
    @roles_accepted('admin')
    def put(self, category_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
        args = parser.parse_args()
        category = Category.query.get(category_id)
        if(category==None):
            return {'message': f'Category_id {category_id} is not in the database'}, 404
        category.name = args['name']
        db.session.commit()
        return {'message': 'Category updated'},200
    



class ProductResource(Resource):
    @auth_required('token','session')
    @roles_accepted('admin')
    def get(self, product_id):
        product = Product.query.get(product_id)
        if(product==None):
            return {'message': f'Product_id {product_id} is not in the database'}, 404
        else:
            return {
                'id': product.id,
                'category_id': product.category_id,
                'name': product.name,
                'manufacturer': product.manufacturer,
                'expiry': str(product.expiry),
                'rate_per_unit': product.rate_per_unit,
                'available_quantity': product.available_quantity,
                'units': product.units,
                'date_added': str(product.date_added)
            }, 200  
    
    @auth_required('token','session')
    @roles_accepted('admin')
    def delete(self, product_id):
        product = Product.query.get(product_id)
        if(product==None):
            return {'message': f'Product_id {product_id} is not in the database'}, 404
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted'},200
    
    @auth_required('token','session')
    @roles_accepted('admin')
    def put(self, product_id):
        product = Product.query.get(product_id)
        if(product==None):
            return {'message': f'Product_id {product_id} is not in the database'}, 404
        parser = reqparse.RequestParser()
        parser.add_argument('category_id', type=int, required=True, help="Category ID cannot be blank!")
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
        parser.add_argument('manufacturer', type=str)
        parser.add_argument('expiry', type=str)
        parser.add_argument('rate_per_unit', type=float, help="Rate cannot be blank!")
        parser.add_argument('available_quantity', type=int, help="quantity cannot be blank!")
        parser.add_argument('units', type=str)
        args = parser.parse_args()
        
        product.category_id = args['category_id']
        product.name = args['name']
        product.manufacturer = args['manufacturer']
        product.expiry = datetime.strptime(args['expiry'],"%Y-%m-%d").date()
        product.rate_per_unit = args['rate_per_unit']
        product.available_quantity = args['available_quantity']
        product.units = args['units']
        db.session.commit()
        return {'message': 'Product updated'},200
    
    

class CategoryListResource(Resource):
    #list out all the  categories
    @auth_required('token','session')
    @roles_accepted('admin')
    @marshal_with(category_fields)
    def get(self):
        return Category.query.all()
    
    #create a new category
    @auth_required('token','session')
    @roles_accepted('admin')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
        args = parser.parse_args()
        new_category = Category(name=args['name'])
        db.session.add(new_category)
        db.session.commit()
        return {'message': 'Category created successfully'}, 201

class ProductListResource(Resource):
    @auth_required('token','session')
    @roles_accepted('admin')
    @marshal_with(product_fields)
    def get(self):
        return Product.query.all()

    @auth_required('token','session')
    @roles_accepted('admin')
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('category_id', type=int, required=True, help="Category ID cannot be blank!")
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
        parser.add_argument('manufacturer', type=str)
        parser.add_argument('expiry', type=str)
        parser.add_argument('rate_per_unit', type=float, help="Rate cannot be blank!")
        parser.add_argument('available_quantity', type=int, help="quantity cannot be blank!")
        parser.add_argument('units', type=str)
        args = parser.parse_args()
        c_id = args['category_id']
        if(Category.query.get(c_id)==None):
            return {'message': f'Category_id {c_id} is not in the database'}, 404
        new_product = Product(
            category_id=args['category_id'],
            name=args['name'],
            manufacturer=args['manufacturer'],
            expiry=datetime.strptime(args['expiry'],"%Y-%m-%d").date(),
            rate_per_unit=args['rate_per_unit'],
            available_quantity=args['available_quantity'],
            units=args['units']
        )
        db.session.add(new_product)
        db.session.commit()
        return {'message': 'Product added to the category'}, 201
    
class OrderSummary(Resource):
    @auth_required('token', 'session')
    @roles_accepted('admin')
    def get(self):
        orders= Order.query.all()
        l = []
        for order in orders:
            l.append({
                "id":order.id,
                "user_id":order.user_id,
                "placed_at":order.placed_at,
                "description":order.description
            })
        return l, 200

class OrderItemsSummary(Resource):
    @auth_required('token', 'session')
    @roles_accepted('admin')
    def get(self):
        orders= OrderItem.query.all()
        l = []
        for order in orders:
            l.append({
                "id":order.id,
                "order_id":order.order_id,
                "product_id":order.product_id,
                "quantity":order.quantity,
                "total_price":order.total_price
            })
        return l, 200


    
class PlaceOrder(Resource):
    @auth_required('token', 'session')
    @roles_accepted('admin')
    def post(self, user_id):
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return {"message": "No items in the cart to order"}, 400
        new_order = Order(
            user_id=user_id,
            description=request.json.get('description', None) 
        )

        db.session.add(new_order)
        db.session.commit()
        for item in cart_items:
            new_order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.Quantity,
                total_price=item.price_of_qty  # Assuming total_price is part of the JSON request
            )
            product_id = item.product_id
            product =Product.query.filter_by(id = product_id).first()
            product.available_quantity = product.available_quantity - item.Quantity
            db.session.add(new_order_item)
        db.session.commit()
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return {"message": "Order placed successfully"}, 200
    
class CancelOrder(Resource):
    @auth_required('token', 'session')
    @roles_accepted('admin')
    def delete(self, user_id, order_id):
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if order is None:
            return {"message": "Order not found"}, 404
        current_time = datetime.utcnow()
        if (current_time - order.placed_at).total_seconds() > 1800:  # 30 minutes in seconds
            return {"message": "Order cannot be canceled, it's been more than 30 minutes since it was placed"}, 400
        order_items = OrderItem.query.filter_by(order_id=order_id).all()
        for order_item in order_items:
            product_id = order_item.product_id
            product = Product.query.filter_by(id=product_id).first()
            if product:
                product.available_quantity += order_item.quantity
        db.session.commit()
        for order_item in order_items:
            db.session.delete(order_item)
        db.session.delete(order)
        db.session.commit()
        return {"message": "Order canceled successfully"}, 200

api.add_resource(OrderSummary,'/get-orders') 
api.add_resource(OrderItemsSummary,'/get-order-items') 
api.add_resource(PlaceOrder,'/place-order/<int:user_id>')
api.add_resource(CancelOrder,'/cancel-order/<int:user_id>/<int:order_id>')
api.add_resource(CategoryResource, '/categories/<int:category_id>')
api.add_resource(CategoryListResource, '/categories')
api.add_resource(ProductResource, '/products/<int:product_id>')
api.add_resource(ProductListResource, '/products')

# class Admin(Resource):
#     def get(self):
#         return "Hello World"
#     def post(self):