import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TOD uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TOD implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        query = Drink.query.all()
        if len(query) == 0:
            abort(404)
        drinks = [drink.short() for drink in query]
                
        return jsonify({
            'success': True,
            'drinks': drinks
            }), 200
    except:
        abort(422)

'''
@TOD implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try:
        query = Drink.query.all()
        if len(query) == 0:
            abort(404)
        drinks = [drink.long() for drink in query]
                
        return jsonify({
            'success': True,
            'drinks': drinks
            }), 200
    except:
        abort(422)


'''
@TOD implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = json.dumps(body['recipe'])
    try:
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()

        query = Drink.query.all()
        if len(query) == 0:
            abort(404)

        drinks = [drink.long() for drink in query]
                
        return jsonify({
            'success': True,
            'drinks': drinks
            }), 200
    except:
        abort(422)

'''
@TOD implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        
        body = request.get_json()
        drink.title = body.get('title', None)
        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])
            
        drink.update()

    except Exception as e:
        abort(422)
        print('Exception :', e)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200



'''
@TOD implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()
                
        return jsonify({
            'success': True,
            'delete': id
            }), 200
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422

'''
@TOD implement error handlers using the @app.errorhandler(error) decorator
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not Found"
    }), 404

'''
@TOD implement error handler for 404
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"  
        }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not Allowed"   
        }), 405

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Server Error"   
        }), 500

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "Unauthorized"   
        }), 401

'''
@TOD implement error handler for AuthError 401, 403
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, 
        "error": error.status_code,
        "message": "AuthError"   
        }), error.status_code
