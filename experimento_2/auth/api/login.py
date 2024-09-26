from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from models import User, db
from flask import make_response, jsonify

parser = reqparse.RequestParser()
parser.add_argument('username', required=True, help='Username is required')
parser.add_argument('password', required=True, help='Password is required')


class LoginResource(Resource):
    def post(self):
        data = parser.parse_args()
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            # Create access token
            access_token = create_access_token(identity={'username': user.username, 'rol': user.role.value})

            # Create the response body
            response_body = {'message': 'OK'}

            # Create the response object and set the header for the access token
            response = make_response(jsonify(response_body), 200)
            response.headers['Authorization'] = access_token

            return response

        # Return a 401 response if credentials are invalid
        return {'message': 'Invalid credentials'}, 401
