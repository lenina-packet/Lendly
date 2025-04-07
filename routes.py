from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from models import Message, City, CityHistory, Product, Order
from database import session
import random
import string

message_blueprint = Blueprint('messages', __name__)
order_blueprint = Blueprint('orders', __name__)

@message_blueprint.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    new_message = Message(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        text=data['text'],
        timestamp=datetime.utcnow().isoformat()
    )
    session.add(new_message)
    session.commit()
    return jsonify({"status": "Message sent successfully!"}), 201

@message_blueprint.route('/get_messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    messages = session.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).all()
    return jsonify([{"sender_id": m.sender_id, "receiver_id": m.receiver_id, "text": m.text, "timestamp": m.timestamp} for m in messages]), 200

@message_blueprint.route('/get_city_history/<int:product_id>', methods=['GET'])
def get_city_history(product_id):
    city_history = session.query(CityHistory).filter_by(product_id=product_id).all()
    return jsonify([{"latitude": ch.latitude, "longitude": ch.longitude} for ch in city_history]), 200

@order_blueprint.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    data = request.json
    order = session.query(Order).get(order_id)
    if order:
        order.status = data['status']
        session.commit()
    return jsonify({"status": "Order status updated!"}), 200

def generate_tracking_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@order_blueprint.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    new_order = Order(
        status='in transit',
        tracking_number=generate_tracking_number()
    )
    session.add(new_order)
    session.commit()
    return jsonify({"status": "Order created successfully!", "tracking_number": new_order.tracking_number}), 201

# Добавьте остальные маршруты по аналогии, например, для создания продукта и получения городов

@order_blueprint.route('/add_product', methods=['GET', 'POST'])
def add_product():
    # Ваш код для добавления продукта, включая форму
    pass