from api_application import api,app, db, roles_accepted, auth_required
from api_application.models import *
from flask_restful import Resource, reqparse, output_json, reqparse, fields

cart_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'product_id': fields.Integer,
    'quantity': fields.Float,
}

# List all items in the cart for the given user
class CartListResource(Resource):
    @auth_required('token','session')
    @roles_accepted('user','manager')
    def get(self, user_id):
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return {'message': f'No items in the cart for user_id {user_id}'}, 404
        return [{
                'id': cart_item.id,
                'user_id': cart_item.user_id,
                'product_id': cart_item.product_id,
                'product_name': Product.query.filter_by(id = cart_item.product_id).first().name,
                'quantity': cart_item.Quantity,
                'rate_per_unit':cart_item.rate_per_unit,
                'total_price':cart_item.price_of_qty
            } for cart_item in cart_items], 200

# Add,Delete and Update a product to the cart for the given user
class CartResource(Resource):
    @auth_required('token','session')
    @roles_accepted('user','manager')
    def post(self, user_id,product_id):
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', type=float, required=True, help="Quantity cannot be blank!")
        args = parser.parse_args()
        incart = Cart.query.filter_by(user_id = user_id, product_id = product_id).all()
        if(len(incart)!=0):
            return {'message': 'Product already added in the cart'}, 404
        product = Product.query.get(product_id)
        if(product==None):
            return {'message': f'Product_id {product_id} is not in the database'}, 404
        if product.available_quantity < args['quantity']:
            return {'message': f'Product_id {product_id} is not available in the required quantity'}, 404
        new_cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            Quantity=args['quantity'],
            rate_per_unit = product.rate_per_unit,
            price_of_qty = round(product.rate_per_unit*args['quantity'],2)
        )
        db.session.add(new_cart_item)
        db.session.commit()

        return {'message': f'Product added to the cart for user_id {user_id}'}, 200

    @auth_required('token','session')
    @roles_accepted('user','manager')
    def put(self, user_id,product_id):
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', type=float, required=True, help="Quantity cannot be blank!")
        args = parser.parse_args()
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item is None:
            return {'message': f'Product with ID {product_id} not found in the cart for user_id {user_id}'}, 404
        product = Product.query.get(product_id)
        # Update the quantity
        if product.available_quantity < args['quantity']:
            return {'message': f'Product_id {product_id} is not available in the required quantity'}, 404
        cart_item.Quantity = args['quantity']
        cart_item.price_of_qty = round(product.rate_per_unit*args['quantity'],2)
        db.session.commit()

        return {'message': 'success'}, 200

    @auth_required('token','session')
    @roles_accepted('user','manager')
    def delete(self, user_id,product_id):
        parser = reqparse.RequestParser()
        args = parser.parse_args()

        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item is None:
            return {'message': f'Product with ID {product_id} not found in the cart for user_id {user_id}'}, 404

        db.session.delete(cart_item)
        db.session.commit()

        return {'message': 'success'}, 200
    

class PlaceOrder(Resource):
    @auth_required('token','session')
    @roles_accepted('user','manager')
    def post(self, user_id):
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return {"message": "No items in the cart to order"}, 400
        new_order = Order(
            user_id=user_id,
            description=request.json.get('description', None),
            total_amount=0
        )

        db.session.add(new_order)
        db.session.commit()
        total_amount = 0
        for item in cart_items:
            new_order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.Quantity,
                total_price=item.price_of_qty  # Assuming total_price is part of the JSON request
            )
            total_amount += item.price_of_qty
            product_id = item.product_id
            product =Product.query.filter_by(id = product_id).first()
            product.available_quantity = product.available_quantity - item.Quantity
            db.session.add(new_order_item)
        new_order = Order.query.filter_by(id=new_order.id).first()
        new_order.total_amount = total_amount
        db.session.commit()
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return {"message": "success"}, 200
    
class CancelOrder(Resource):
    @auth_required('token','session')
    @roles_accepted('user','manager')
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
        return {"message": "success"}, 200
    
api.add_resource(PlaceOrder,'/place-order/<int:user_id>')
api.add_resource(CancelOrder,'/cancel-order/<int:user_id>/<int:order_id>')
api.add_resource(CartListResource, '/cart/<int:user_id>')
api.add_resource(CartResource, '/cart/<int:user_id>/<int:product_id>')






