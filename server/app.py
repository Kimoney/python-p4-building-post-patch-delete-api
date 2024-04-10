#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import db, User, Review, Game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return "Index for Game/Review/User API"

@app.route('/games')
def games():

    games = []
    for game in Game.query.all():
        game_dict = {
            "title": game.title,
            "genre": game.genre,
            "platform": game.platform,
            "price": game.price,
        }
        games.append(game_dict)

    response = make_response(
        games,
        200
    )

    return response

@app.route('/games/<int:id>')
def game_by_id(id):
    game = Game.query.filter(Game.id == id).first()
    
    game_dict = game.to_dict()

    response = make_response(
        game_dict,
        200
    )

    return response

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    
    if request.method == 'GET':
        reviews = []
        for review in Review.query.all():
            review_dict = review.to_dict()
            reviews.append(review_dict)

        response = make_response(
            reviews,
            200
        )
        return response
# use elif instead of else because of returning errors like 404 et al.   
    elif request.method == 'POST':
        new_review = Review(
            score=request.form.get('score'),
            comment=request.form.get('comment'),
            game_id=request.form.get('game_id'),
            user_id=request.form.get('user_id'),
        )
# Commit Changes to db
        db.session.add(new_review)
        db.session.commit()
# Convert to json and return resp of newly created review
# We create review_dict after committing the review to the database,
# As this populates it with an ID and data from its game and user
        review_dict = new_review.to_dict()
        resp = make_response(review_dict, 201)
        print(resp)

        return resp

@app.route('/users')
def users():

    users = []
    for user in User.query.all():
        user_dict = user.to_dict()
        users.append(user_dict)

    response = make_response(
        users,
        200
    )

    return response

@app.route('/reviews/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def review_by_id(id):
    review = Review.query.filter(Review.id == id).first()

    if request.method == 'GET':
        review_dict = review.to_dict()

        resp = make_response(review_dict, 200)
        return resp
    
    elif request.method == 'DELETE':
        db.session.delete(review)
        db.session.commit()

        repsonse_body = {
            "delete_successful": True,
            'message': "Review Deleted!"
        }
        resp = make_response(repsonse_body, 200)
        return resp
    
    elif request.method == 'PATCH':
        for attr in request.form:
            setattr(review, attr, request.form.get(attr))

        db.session.add(review)
        db.session.commit()

        review_dict = review.to_dict()
        resp = make_response(review_dict, 200)

        return resp

if __name__ == '__main__':
    app.run(port=5555, debug=True)
