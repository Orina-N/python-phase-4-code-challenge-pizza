#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET", "POST"])
def restaurants():
    if request.method == "GET":
        restaurants = Restaurant.query.all()
        restaurants_dict = [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants]
        response = make_response(jsonify(restaurants_dict), 200)
        return response

    elif request.method == "POST":
        restaurant = Restaurant(
            name=request.json.get("name"),
            address=request.json.get("address")
        )
        db.session.add(restaurant)
        db.session.commit()
        response = make_response(jsonify(restaurant.to_dict()), 201)
        return response


@app.route("/restaurants/<int:id>", methods=["GET", "PATCH", "DELETE"])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if restaurant:
        if request.method == "GET":
            response = make_response(jsonify(restaurant.to_dict()),
                                      200)
            return response
        
        elif request.method == "PATCH":
            for attr in request.json:
                setattr(restaurant, attr, request.json.get(attr))
            db.session.add(restaurant)
            db.session.commit()

            response = make_response(jsonify(restaurant.to_dict()), 200)
            return response
        
        elif request.method == "DELETE":
            db.session.delete(restaurant)
            db.session.commit()

            response = make_response({}, 204)
            return response
    
    else:
        message = {"error": "Restaurant not found"}
        return make_response(jsonify(message), 404)


@app.route("/pizzas", methods=["GET", "POST"])
def pizzas():
    if request.method == "GET":
        pizzas = Pizza.query.all()
        pizzas_dict = [pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas]
        response = make_response(jsonify(pizzas_dict), 200)
        return response
    
    elif request.method == "POST":
        pizza = Pizza(
            name=request.json.get("name"),
            ingredients=request.json.get("ingredients")
        )
        db.session.add(pizza)
        db.session.commit()
        response = make_response(jsonify(pizza.to_dict()), 201)
        return response


@app.route("/restaurant_pizzas", methods=["GET", "POST"])
def restaurant_pizzas():
    if request.method == "GET":
        restaurant_pizzas = RestaurantPizza.query.all()
        restaurant_pizzas_dict = [restaurant_pizza.to_dict() for restaurant_pizza in restaurant_pizzas]
        response = make_response(jsonify(restaurant_pizzas_dict), 200)
        return response
    
    elif request.method == "POST":
        try:
            price = request.json.get("price")
            if not (1 <= price <= 30):
                raise ValueError("validation errors")

            restaurant_pizza = RestaurantPizza(
                price=price,
                restaurant_id=request.json.get("restaurant_id"),
                pizza_id=request.json.get("pizza_id")
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            response = make_response(jsonify(restaurant_pizza.to_dict()), 201)
            return response
        
        except ValueError as e:
            message = {"errors": [str(e)]}
            response = make_response(jsonify(message), 400)
            return response


@app.route("/pizzas/<int:id>", methods=["GET", "PATCH", "DELETE"])
def pizza_by_id(id):
    pizza = Pizza.query.filter(Pizza.id == id).first()
    if pizza:
        if request.method == "GET":
            response = make_response(jsonify(pizza.to_dict()), 200)
            return response
        
        elif request.method == "PATCH":
            for attr in request.json:
                setattr(pizza, attr, request.json.get(attr))
            db.session.add(pizza)
            db.session.commit()
            response = make_response(jsonify(pizza.to_dict()), 200)
            return response
        
        elif request.method == "DELETE":
            db.session.delete(pizza)
            db.session.commit()
            response = make_response({}, 204)
            return response
    
    else:
        message = {"error": f"Pizza {id} not found."}
        response = make_response(jsonify(message), 404)
        return response

if __name__ == "__main__":
    app.run(port=5555, debug=True)