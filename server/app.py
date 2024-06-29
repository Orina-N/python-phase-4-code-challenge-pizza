#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, request

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def get_restaurants():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name
        }
        restaurants.append(restaurant_dict)
    return jsonify(restaurants)

@app.route("/restaurants/<int:id>",methods=['GET','DELETE'])
def get_restaurant(id):
    if request.method == 'GET':
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
    
        restaurant_pizzas = []
        for rpizza in restaurant.restaurant_pizzas:
            pizza_data = {
                "id": rpizza.id,
                "pizza": {
                    "id": rpizza.pizza.id,
                    "name": rpizza.pizza.name,
                    "ingredients": rpizza.pizza.ingredients
                },
                "price": rpizza.price,
                "pizza_id": rpizza.pizza_id,
                "restaurant_id": rpizza.restaurant_id
            }
            restaurant_pizzas.append(pizza_data)
    
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
            "restaurant_pizzas": restaurant_pizzas
        }
    
        return jsonify(restaurant_dict)
    
    elif request.method == 'DELETE':
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        
        db.session.delete(restaurant)
        db.session.commit()

        return '', 204

@app.route('/pizzas',methods=['GET'])
def get_pizzas():
    if request.method == 'GET':
        pizzas = Pizza.query.all()
        pizza_list = []
        for pizza in pizzas:
            pizza_dict = {
                "id": pizza.id,
                "ingredients": pizza.ingredients,
                "name": pizza.name
            }
            pizza_list.append(pizza_dict)
        return jsonify(pizza_list)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
