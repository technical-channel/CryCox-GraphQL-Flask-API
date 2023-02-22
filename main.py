
from api.queries import (resolve_user, resolve_getLivePrice, resolve_all_offers, resolve_offer_by_id, resolve_userinfo_by_id,
                         resolve_trade_by_offer_id, resolve_userBalance_by_id, resolve_trade_by_trade_id, resolve_offer_by_userId,
                         resolve_trade_by_userId, resolve_depositeHistory_by_UserId, resolve_check_metamask, resolve_check_email_otp)
from api import app, db
from flask_cors import CORS
from flask import Flask, request, session

from ariadne import load_schema_from_path, make_executable_schema, graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify

from api.mutations import (resolve_update_info, resolve_create_trade,
                           resolve_register_user, resolve_give_feedback, resolve_deposite_fund,
                           resolve_create_offer, resolve_password_change, resolve_send_otp, resolve_update_tradeInfo_by_tradeId,
                           resolve_loginUser, resolve_check_session, resolve_verify_otp, resolve_register_metamask, resolve_send_email_otp, resolve_delete_offerById)

from functools import wraps
import uuid  # for public id
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, make_response
import jwt
from datetime import datetime, timedelta
from api.models import Test

app = Flask(__name__)


CORS(app)

query = ObjectType("Query")
mutation = ObjectType("Mutation")

# API- 1. Live Price Fetch
query.set_field("priceConvert", resolve_getLivePrice)
query.set_field("user", resolve_user)

# API-5 - All Offers (filter)
query.set_field("filterOffers", resolve_all_offers)
# API-5 Offer By Id
query.set_field("offerById", resolve_offer_by_id)
# query.set_field("userInfo", resolve_userInfo)
# API-8 Feedback by offer id
query.set_field("tradeByOfferID", resolve_trade_by_offer_id)
# API-9 User info By user Id
query.set_field("userInfoById", resolve_userinfo_by_id)
# API-16 Fetch User Balance by user id
query.set_field("userBalanceByUserId", resolve_userBalance_by_id)
query.set_field("tradeByTradeId", resolve_trade_by_trade_id)
query.set_field("offerByUserId", resolve_offer_by_userId)
query.set_field("tradeByUserId", resolve_trade_by_userId)
query.set_field("depositeHistoryByUserId",
                resolve_depositeHistory_by_UserId)
query.set_field("isMetamaskExist", resolve_check_metamask)
query.set_field("verifyEmailOTP", resolve_check_email_otp)
mutation.set_field("test", resolve_check_session)

# API-2. Login API
mutation.set_field("userLogin", resolve_loginUser)
# API-4. Signup API
mutation.set_field("registerUser", resolve_register_user)
# mutation.set_field("createTodo", resolve_create_todo)
mutation.set_field("updateInfo", resolve_update_info)
# mutation.set_field("deleteTodo", resolve_delete_todo)
# mutation.set_field("updateDueDate", resolve_update_due_date)
# mutation.set_field("createUserInfo", resolve_user_info)
# API-7 Trade (Create New Trade Buy Or Sell)
mutation.set_field("createTrade", resolve_create_trade)
# API-10. Create New Offer
mutation.set_field("createOffer", resolve_create_offer)
mutation.set_field("giveFeedback", resolve_give_feedback)
mutation.set_field("depositeFund", resolve_deposite_fund)
mutation.set_field("changePassword", resolve_password_change)
mutation.set_field("sendOTP", resolve_send_otp)
mutation.set_field("sendEmailOTP", resolve_send_email_otp)
mutation.set_field("verifyOTP", resolve_verify_otp)
mutation.set_field("updateTradeInfoByTradeID",
                   resolve_update_tradeInfo_by_tradeId)
mutation.set_field("registerMetamask", resolve_register_metamask)
mutation.set_field("deleteOfferByOfferId", resolve_delete_offerById)

# mutation.set_field("testSignup", resolve_test_signup)
# mutation.set_field("testLogin", resolve_test_login)
# mutation.set_field("createDepositRequest", resolve_create_deposit_request)


type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


@app.route('/check-session-user')
def rahul():
    return str(session['username'])


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Test.objects(
                public_id=data['public_id']).first()
        except Exception as e:
            print("Error Msg : ", e)
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)
    return decorated


# signup route
@app.route('/signup', methods=['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.form

    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')

    # checking for existing user
    user = Test.objects(email=email).first()
    if not user:
        # database ORM object  if Registration.objects(email= 'ritik@gmail.com').first():

        user = user = Test(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password)
        ).save()

        user.public_id = str(user.id)
        user.save()

        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)


# Login Route
@app.route('/login', methods=['POST'])
def login():
    # creates dictionary of form data
    auth = request.form

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = Test.objects(email=auth.get('email')).first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=5)
        }, app.config['SECRET_KEY'])

        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


# User
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = Test.objects.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email
        })

    return jsonify({'users': output})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8955)
