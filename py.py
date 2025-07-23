from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database sozlamalari
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELLAR
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)

class SavedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item = db.Column(db.String(200), nullable=False)

# DB yaratish
with app.app_context():
    db.create_all()

# ------------------- USER ROUTES -------------------

@app.route("/users/", methods=["POST"])
def create_user():
    data = request.json
    if not data or "name" not in data:
        abort(400, "Name is required")
    
    user = User(name=data["name"], address=data.get("address"))
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name, "address": user.address})

@app.route("/users/<int:user_id>", methods=["GET"])
def read_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, "User not found")
    return jsonify({"id": user.id, "name": user.name, "address": user.address})

@app.route("/users/<int:user_id>/address", methods=["PUT"])
def update_address(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, "User not found")
    data = request.json
    address = data.get("address")
    if not address:
        abort(400, "Address required")
    user.address = address
    db.session.commit()
    return jsonify({"message": "Address updated", "address": address})

@app.route("/users/<int:user_id>/address", methods=["DELETE"])
def delete_address(user_id):
    user = User.query.get(user_id)
    if not user or not user.address:
        abort(404, "Address not found")
    user.address = None
    db.session.commit()
    return jsonify({"message": "Address deleted"})

# ------------------- SAVED ITEMS ROUTES -------------------

@app.route("/users/<int:user_id>/items/", methods=["POST"])
def add_saved_item(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, "User not found")
    data = request.json
    item_name = data.get("item")
    if not item_name:
        abort(400, "Item required")
    saved_item = SavedItem(user_id=user_id, item=item_name)
    db.session.add(saved_item)
    db.session.commit()
    return jsonify({"id": saved_item.id, "user_id": user_id, "item": saved_item.item})

@app.route("/users/<int:user_id>/items/", methods=["GET"])
def get_saved_items(user_id):
    items = SavedItem.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": item.id, "user_id": item.user_id, "item": item.item}
        for item in items
    ])

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_saved_item(item_id):
    item = SavedItem.query.get(item_id)
    if not item:
        abort(404, "Item not found")
    data = request.json
    new_item = data.get("item")
    if not new_item:
        abort(400, "Item required")
    item.item = new_item
    db.session.commit()
    return jsonify({"message": "Item updated", "item": new_item})

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_saved_item(item_id):
    item = SavedItem.query.get(item_id)
    if not item:
        abort(404, "Item not found")
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"})

# RUN
if __name__ == "__main__":
    app.run(debug=True)
