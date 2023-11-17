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
    @auth_required('token', 'session')
    @roles_accepted('user')
    def get(self, user_id):
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return {'message': f'No items in the cart for user_id {user_id}'}, 404
        return [{
                'id': cart_item.id,
                'user_id': cart_item.user_id,
                'product_id': cart_item.product_id,
                'quantity': cart_item.Quantity
            } for cart_item in cart_items], 200

# Add,Delete and Update a product to the cart for the given user
class CartResource(Resource):
    @auth_required('token', 'session')
    @roles_accepted('user')
    def post(self, user_id,product_id):
        
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', type=float, required=True, help="Quantity cannot be blank!")
        args = parser.parse_args()

        product = Product.query.get(product_id)
        if(product==None):
            return {'message': f'Product_id {product_id} is not in the database'}, 404

        new_cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            Quantity=args['quantity']
        )
        db.session.add(new_cart_item)
        db.session.commit()

        return {'message': f'Product added to the cart for user_id {user_id}'}, 200

    @auth_required('token', 'session')
    @roles_accepted('user')
    def put(self, user_id,product_id):
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', type=float, required=True, help="Quantity cannot be blank!")
        args = parser.parse_args()

        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item is None:
            return {'message': f'Product with ID {product_id} not found in the cart for user_id {user_id}'}, 404

        # Update the quantity
        cart_item.Quantity = args['quantity']
        db.session.commit()

        return {'message': f'Cart updated for user_id {user_id}'}, 200

    @auth_required('token', 'session')
    @roles_accepted('user')
    def delete(self, user_id,product_id):
        parser = reqparse.RequestParser()
        args = parser.parse_args()

        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item is None:
            return {'message': f'Product with ID {product_id} not found in the cart for user_id {user_id}'}, 404

        db.session.delete(cart_item)
        db.session.commit()

        return {'message': f'Product deleted from the cart for user_id {user_id}'}, 200
    

api.add_resource(CartListResource, '/cart/<int:user_id>')
api.add_resource(CartResource, '/cart/<int:user_id>/<int:product_id>')



