
import requests
import random
from datetime import datetime
from api import app, db
from api.models import Registration, UserInfo, Trade, CreateOffer, DepositeAssets, Assets, OTP, Test, DepositeRequest
from flask import session
import os
from twilio.rest import Client
from functools import wraps
import jwt
from datetime import datetime, timedelta
from api.models import Test
from mongoengine.queryset.visitor import Q
import os
import json
from time import time
from dotenv import load_dotenv
load_dotenv()

# app = app()


# print("app : ", app, dir(app.session_interface), type(app.session_interface))

phone_number = os.getenv("MYPHONENUMBER")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_sid = os.getenv("TWILIO_VERIFY_SID")


MAIL_GUN_API = os.getenv("MAIL_GUN_API")
DOMAIN_NAME = os.getenv("DOMAIN_NAME")


API_KEY = os.getenv("API_KEY")
API_SEC = os.getenv("API_SEC")


# def resolve_createMeeting(obj, info, topic):
#     try:
#         (join_URL, meetingPassword) = createMeeting(topic)
#         payload = {
#             "success": True,
#             "data": [join_URL, meetingPassword]
#         }
#     except:
#         payload = {
#             "success": False,
#             "errors": [f"Unable to Start Meeting"]
#         }
#     return payload


# Delete Offer by Offer ID
def resolve_delete_offerById(obj, info, offer_id):
    try:
        offer = CreateOffer.objects.with_id(offer_id)
        offer.delete()
        payload = {
            "success": True,
            "offer": [offer.to_dict()]
        }
    except:
        payload = {
            "success": False,
            "errors": [f"Given Offer id {offer_id} not fount"]
        }
    return payload


# register metamask address for the user
def resolve_register_metamask(obj, info, user_id, metamask):
    try:
        existUser = Registration.objects.with_id(user_id)
        if not existUser:
            payload = {
                "success": False,
                "errors": [f"User matching id {user_id} not found"]
            }
        user = Registration.objects(metamask=metamask).first()
        if user:
            payload = {
                "success": False,
                "errors": [f"Metamask id '{metamask}' Already Register"]
            }
        else:
            existUser.metamask = metamask
            existUser.save()
            session.add(existUser)
            session.commit()
            print(session, dir(session))
        payload = {
            "success": True,
            "user": [existUser.to_dict()]
        }
        return payload
    except Exception as e:  # trade not found
        payload = {
            "success": False,
            "errors": [f"Graph QL Error : {e}"]
        }
    return payload


# API-4. Signup API
def resolve_register_user(obj, info, password, username, metamask, email="", phone=""):
    def create_on_success():
        # User Info Table
        meta = {'collection': 'userinfo'}
        userInfo = UserInfo(user_id=user.id, username=username)
        userInfo.save()

        # Assets Table
        meta = {'collection': 'assets'}
        assets = Assets(user_id=user.id)
        assets.save()

    try:
        if email.strip() == "" and phone.strip() == "" and username.strip() == "" and metamask.strip() == "":
            payload = {
                "success": False,
                "errors": ["Invalid Input"]
            }
            return payload

        # check user is already exist or not
        user = Registration.objects(
            (Q(email=email) | Q(phone=phone) | Q(username=username) | Q(metamask=metamask))).first()
        if user:
            payload = {
                "success": False,
                "errors": ["User Alredy Exist"]
            }

        else:  # when user already not exist
            meta = {'collection': 'registration'}
            if email:
                user = Registration(
                    email=email.lower(), password=password, username=username, metamask=metamask)
                user.save()
                create_on_success()
                payload = {
                    "success": True,
                    "user": [user.to_dict()]
                }
            elif phone:
                user = Registration(
                    phone=phone, password=password, username=username, metamask=metamask)
                user.save()
                create_on_success()
                payload = {
                    "success": True,
                    "user": [user.to_dict()]
                }
            else:
                payload = {
                    "success": False,
                    "errors": ["Internal Server Error"]
                }

    except Exception as e:  # date time errors
        payload = {
            "success": False,
            "errors": [f"Graph QL Error : {e}"]
        }
    return payload


def resolve_send_email_otp(obj, info, to_email):
    try:
        otp = str(int(random.random()*10**6))
        msg = f"Hello User, Your OTP is {otp}."
        res = requests.post(f"https://api.mailgun.net/v3/{DOMAIN_NAME}/messages",
                            auth=("api", MAIL_GUN_API),
                            data={"from": "Rahul Saini <rahul.saini@ramlogics.com>",
                                  "to": [to_email],
                                  "subject": "Registeration OTP",
                                  "text": msg
                                  }
                            )
        if res.status_code == 200:
            user = OTP.objects(email__iexact=to_email).first()
            if user:
                user.otp = otp
                user.updated_at = datetime.now()
                user.save()
            else:
                user = OTP(email=to_email, otp=otp, updated_at=datetime.now())
                user.save()
            payload = {
                "success": True,
                "message": [f"OTP Send sucessfully"],
                "status": [res.status_code],
                "data": [otp]
            }
        else:
            payload = {
                "success": False,
                "message": [f"Unable to send OTP"],
                "status": [res.status_code]
            }
        return payload
    except Exception as e:
        payload = {
            "success": False,
            "errors":  [f"Graph QL Error : {e}"]
        }
        return payload


def resolve_check_session(obj, info):
    try:
        # print(dir(session))
        print("session['username'] : ", session.items())
        data = str(session['username'])
        payload = {
            "success": True,
            "errors": [data]
        }
    except:
        data = "Nothing"
        payload = {
            "success": False,
            "errors": [str(session.items())]
        }
    return payload


# Login Route
def resolve_loginUser(obj, info,  password, email="", phone=""):
    session.modified = True
    user = Registration.objects(
        (Q(email__iexact=email) | Q(phone__iexact=phone))).first()
    if not user:
        payload = {
            "success": False,
            "errors": ["User does not exist !!."],
            "token": ""
        }
        return payload
    if user.password == password:
        # generates the JWT Token
        token = jwt.encode({
            'username': user.username,
            'exp': datetime.now() + timedelta(minutes=5)
        }, app.config['SECRET_KEY'])

        session.clear()
        session['username'] = user.username
        print("session['username'] : ", session['username'])
        print(session, type(session))
        print("Session Dir : ", dir(session))
        session.modified = True

        payload = {
            "success": True,
            "user": [user.to_dict()],
            "token": token.decode('UTF-8')
        }
        return payload

        # return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    payload = {
        "success": False,
        "errors": ["Wrong Password !!"],
        "token": "Could not verify"
    }
    return payload


# # API-2. Login API
# def resolve_loginUser(obj, info, email="", phone="", password=""):
#     try:
#         user = []
#         if email.split() != "":
#             user = Registration.objects(
#                 email=email.lower(), password=password)
#         elif phone.split() != "":
#             user = Registration.objects(
#                 phone=phone, password=password)
#         else:
#             payload = {
#                 "success": False,
#                 "errors":  ["Phone or Email, atleast one entry must be there."]
#             }

#         if user:
#             payload = {
#                 "success": True,
#                 "user": user[0].to_dict()
#             }
#         else:
#             payload = {
#                 "success": False,
#                 "errors":  ["Invalid Credintial"]
#             }
#     except AttributeError:
#         payload = {
#             "success": False,
#             "errors":  [f"User not  matching"]
#         }

#     return payload


# Update trade info by trade id
def resolve_update_tradeInfo_by_tradeId(obj, info, trade_id, **kwargs):
    print(kwargs.items(), "Kwards Items ")
    print(list(kwargs.keys())[0])
    try:
        if len(kwargs.keys()) == 1:
            key, value = list(kwargs.keys())[0], list(kwargs.values())[0]
            trade = Trade.objects.with_id(trade_id)
            try:
                trade[str(key)] = value.lower()
                trade.save()
            except:
                trade[str(key)] = value
                trade.save()

            payload = {
                "success": True,
                "trade": [trade.to_dict()]
            }

        else:
            payload = {
                "success": False,
                "errors":  ["Must be change single inforation."]
            }

    except AttributeError as error:
        payload = {
            "success": False,
            "errors":  [f"Trade matching id {trade_id} was not found"]
        }

    return payload


# def resolve_user_info(obj, info, username, bio):
#     try:
#         meta = {'collection': 'userinfo'}

#         userInfo = UserInfo(
#             username=username.lower(), bio=bio.lower()
#         )
#         userInfo.save()
#         payload = {
#             "success": True,
#             "info": userInfo.to_dict()
#         }
#     except ValueError as e:  # date time errors
#         payload = {
#             "success": False,
#             "errors": [f"Incorrect input data : {e}"]
#         }

#     return payload


def resolve_update_info(obj, info, user_id, **kwargs):
    try:
        print("kwargs : ", kwargs)
        meta = {'collection': 'userinfo'}
        userInfo = UserInfo.objects(user_id=user_id)[0]

        # try to change Image
        try:
            print("In Image")
            userInfo.image = kwargs["image"].lower()
        except KeyError:
            pass
        # try to change Bio
        try:
            userInfo.bio = kwargs["bio"].lower()
        except KeyError:
            pass

        # try to change Username
        try:
            userInfo.username = kwargs["username"]
        except KeyError:
            pass

        # try to change PreferredCurrncy
        try:
            userInfo.preferred_currency = kwargs["preferred_currency"].lower()
        except KeyError:
            pass

        # try to change Language
        try:
            userInfo.language = kwargs["language"].lower()
        except KeyError:
            pass

        # try to change is_email_verified
        try:
            print("In is_email_verified", kwargs["is_email_verified"])
            userInfo.is_email_verified = kwargs["is_email_verified"].lower()
        except KeyError:
            pass

        try:
            print("In is_number_verified", kwargs["is_number_verified"])
            userInfo.is_number_verified = kwargs["is_number_verified"].lower()
        except KeyError:
            pass

        userInfo.save()
        payload = {
            "success": True,
            "info": userInfo.to_dict()
        }
    except:
        payload = {
            "success": False,
            "errors":  [f"User matching id {user_id} was not found"]
        }

    return payload


# API-7 Trade (Create New Trade Buy Or Sell)
def resolve_create_trade(obj, info, offer_id, buyer_id, seller_id, cryptocurrency, crypto_trade_amount, fiat_trade_amount, trade_rate, trade_time, trade_type, trade_outcome, pay_via):
    try:
        meta = {'collection': 'trade'}
        trade = Trade(offer_id=offer_id,
                      buyer_id=buyer_id,
                      seller_id=seller_id,
                      cryptocurrency=cryptocurrency.lower(),
                      crypto_trade_amount=crypto_trade_amount,
                      fiat_trade_amount=fiat_trade_amount,
                      trade_rate=trade_rate,
                      trade_time=trade_time,
                      trade_type=trade_type,
                      trade_outcome=trade_outcome.lower(),
                      pay_via=pay_via.lower())
        trade.save()
        (join_URL, meetingPassword) = createMeeting(str(trade.id))
        payload = {
            "success": True,
            "trade": [trade.to_dict()],
            "data": [join_URL, meetingPassword]
        }
    except Exception as e:
        payload = {
            "success": False,
            "errors": ["Internal Servar Error", e]
        }
    return payload


# API-10. Create New Offer
def resolve_create_offer(obj, info, user_id, crypto_name, price_type, offer_type, payment_type, preferred_currency, offer_tags, offer_margin, offerer_verified, min_purchase, max_purchase, offer_price, offer_time_minute, offer_label, offer_terms, offer_condition, offer_location, offer_owner_location):
    try:
        meta = {'collection': 'offer'}
        offer = CreateOffer(
            user_id=user_id,
            crypto_name=crypto_name.lower(),
            price_type=price_type.lower(),
            offer_type=offer_type.lower(),
            payment_type=payment_type,
            preferred_currency=preferred_currency.lower(),
            offer_tags=offer_tags,
            offerer_verified=offerer_verified,
            min_purchase=min_purchase,
            max_purchase=max_purchase,
            offer_price=offer_price,
            offer_margin=offer_margin,
            offer_time_minute=offer_time_minute,
            offer_label=offer_label.lower(),
            offer_terms=offer_terms.lower(),
            offer_condition=offer_condition.lower(),
            offer_location=offer_location.lower(),
            offer_owner_location=offer_owner_location.lower()
        )
        offer.save()
        payload = {
            "success": True,
            "offer": [offer.to_dict()]
        }
    except ValueError as e:  # date time errors
        payload = {
            "success": False,
            "errors": [f"Graph QL Error : {e}"]
        }
    return payload


def resolve_give_feedback(obj, info, trade_id, **kwargs):
    print("giveFeedback is just called")
    print("kwargs : ", kwargs)
    try:
        meta = {'collection': 'trade'}
        trade = Trade.objects.with_id(trade_id)

        print("\n\n\nrade : ", trade, "\n\n\n")

        # try to change buyer_feedback
        try:
            trade.buyer_feedback = kwargs["buyer_feedback"].lower()
        except KeyError:
            pass

        # try to change seller_feedback
        try:
            trade.seller_feedback = kwargs["seller_feedback"].lower()
        except KeyError:
            pass

        # try to change buyer_feedback_text
        try:
            trade.buyer_feedback_text = kwargs["buyer_feedback_text"].lower()
        except KeyError:
            pass

        # try to change seller_feedback_text
        try:
            trade.seller_feedback_text = kwargs["seller_feedback_text"].lower()
        except KeyError:
            pass

        trade.save()
        payload = {
            "success": True,
            "trade": [trade.to_dict()]
        }
    except ValueError as e:  # date time errors
        payload = {
            "success": False,
            "errors": [f"{trade_id} is not a valid trade ID"]
        }
    return payload


def resolve_deposite_fund(obj, info, user_id, assets_name, assets_amount):
    try:
        meta = {'collection': 'deposite'}
        deposite = DepositeAssets(
            user_id=user_id, assets_name=assets_name.lower(), assets_amount=assets_amount
        )
        deposite.save()

        # update in assets table also
        meta = {'collection': 'assets'}
        userInfo = Assets.objects(user_id=user_id)[0]
        print("userInfo : ", userInfo)
        # try to change Image
        if assets_name.upper() == "BTC":
            userInfo.btc += assets_amount
            userInfo.save()
        elif assets_name.upper() == "ETH":
            userInfo.eth += assets_amount
            userInfo.save()
        elif assets_name.upper() == "BNB":
            userInfo.bnb += assets_amount
            userInfo.save()
        elif assets_name.upper() == "SHIB":
            userInfo.shiba += assets_amount
            userInfo.save()
        elif assets_name.upper() == "DOGE":
            userInfo.doge += assets_amount
            userInfo.save()
        elif assets_name.upper() == "USDTERC":
            userInfo.usdt_eth += assets_amount
            userInfo.save()
        elif assets_name.upper() == "USDTBEP":
            userInfo.usdt_bnb += assets_amount
            userInfo.save()

        payload = {
            "success": True,
            "deposite": [deposite.to_dict()]
        }
    except ValueError as e:  # date time errors
        payload = {
            "success": False,
            "errors": ["User Id not Found or Internal Server Error"]
        }
    return payload


# API-3 - Forget Password
def resolve_password_change(obj, info, id, new_password, old_password=""):
    try:
        userInfo = Registration.objects(id=id)[0]

        # when
        # when old_password null then set new password
        if old_password == "" and new_password != "":
            userInfo.password = new_password
            userInfo.save()
            payload = {
                "success": True,
                "user": [userInfo.to_dict()]
            }
            return payload

        # check if old password means, set new password using old password
        elif old_password != "" and new_password != "":
            print("Old password to new")
            if userInfo.password == old_password:
                print("old password match, set new one")
                userInfo.password = new_password
                userInfo.save()
                payload = {
                    "success": True,
                    "user": [userInfo.to_dict()]
                }
                return payload
            else:
                payload = {
                    "success": False,
                    "errors":  [f"Old Password is not matching for user id {id}."]
                }
                return payload

        else:
            payload = {
                "success": False,
                "errors":  [f"wrong input parameters atlest new password required"]
            }
            return payload

    except:
        payload = {
            "success": False,
            "errors":  [f"User matching id {id} was not found, or wrong input parameters"]
        }

        return payload


def resolve_send_otp(obj, info, user_id):
    try:
        user = Registration.objects.with_id(user_id)
        if user:
            # Do next
            if user.phone == "":
                payload = {
                    "success": False,
                    "errors":  [f"Phone Number not found for user id {user_id}"]
                }
            else:
                client = Client(account_sid, auth_token)
                verification = client.verify.v2.services(
                    verify_sid).verifications.create(to=user.phone, channel='sms')
                if verification.status.lower() == "pending":
                    payload = {
                        "success": True,
                        "message": [f"OTP Send sucessfully"],
                        "status": [verification.status.lower()],
                        "user": [user.to_dict()]
                    }
                else:
                    payload = {
                        "success": False,
                        "message": [f"Unable to send OTP"],
                        "status": [verification.status.lower()],
                    }

        else:
            payload = {
                "success": False,
                "message": [f"User id {user_id} not fund "]
            }
        return payload

    except Exception as e:
        payload = {
            "success": False,
            "errors":  [f"Graph QL Error : {e}"],
            "message": [f"Unable to send OTP"]
        }
        return payload


def resolve_verify_otp(obj, info, user_id, otp):
    try:
        user = Registration.objects.with_id(user_id)
        if user:
            # Do next
            if user.phone == "":
                payload = {
                    "success": False,
                    "errors":  [f"Phone Number not found for user id {user_id}"]
                }
            else:
                # verificationStatus = verifyTwilioOTP(str(otp), user.phone)
                client = Client(account_sid, auth_token)
                verification_check = client.verify.v2.services(
                    verify_sid).verification_checks.create(to=user.phone, code=otp)
                if verification_check.status.lower() == "approved":
                    payload = {
                        "success": True,
                        "message": [f"OTP Send sucessfully, verificationStatus : {verification_check.status}"],
                        "status": [verification_check.status.lower()],
                        "user": [user.to_dict()]
                    }
                else:
                    payload = {
                        "success": False,
                        "message": [f"Unable to Verify OTP"],
                        "status": [verification_check.status.lower()]
                    }

        else:
            payload = {
                "success": False,
                "errors": [f"User id {user_id} not fund "]
            }
        return payload

    except Exception as e:
        payload = {
            "success": False,
            "errors":  [f"Graph QL Error : {e}"]
        }
        return payload


def generateToken():
    token = jwt.encode(

        # Create a payload of the token containing
        # API Key & expiration time
        {'iss': API_KEY, 'exp': time() + 5000},

        # Secret used to generate token signature
        API_SEC,

        # Specify the hashing alg
        algorithm='HS256'
    )
    return token.decode('utf-8')


def createMeeting(meetingId):
    # create json data for post requests
    meetingdetails = {"topic": meetingId,
                      "type": 2,
                      "start_time": "2019-06-14T10: 21: 57",
                      "duration": "45",
                      "timezone": "Europe/Madrid",
                      "agenda": "This Meeting Recorded by CryCox Meet",
                      "auto_recording": "local",

                      "recurrence": {"type": 1,
                                     "repeat_interval": 1
                                     },
                      "settings": {"host_video": "true",
                                   "participant_video": "true",
                                   "join_before_host": "False",
                                   "mute_upon_entry": "False",
                                   "watermark": "true",
                                   "audio": "voip",
                                   "auto_recording": "cloud",
                                   "auto_recording": "local",
                                   }
                      }

    headers = {'authorization': 'Bearer ' + generateToken(),
               'content-type': 'application/json'}
    r = requests.post(
        f'https://api.zoom.us/v2/users/me/meetings',
        headers=headers, data=json.dumps(meetingdetails))

    print("\n creating zoom meeting ... \n")
    # print(r.text)
    # converting the output into json and extracting the details
    y = json.loads(r.text)
    join_URL = y["join_url"]
    meetingPassword = y["password"]

    print(
            f'\n here is your zoom meeting link {join_URL} and your \
		password: "{meetingPassword}"\n')
    return (join_URL, meetingPassword)

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         # jwt is passed in the request header
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#         # return 401 if token is not passed
#         if not token:
#             return jsonify({'message': 'Token is missing !!'}), 401
#         try:
#             # decoding the payload to fetch the stored details
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#             current_user = Test.objects(
#                 public_id=data['public_id']).first()
#         except Exception as e:
#             print("Error Msg : ", e)
#             return jsonify({
#                 'message': 'Token is invalid !!'
#             }), 401
#         # returns the current logged in users contex to the routes
#         return f(current_user, *args, **kwargs)
#     return decorated


# # Create Deposite Request
# def resolve_create_deposit_request(obj, info, user_id, crypto_name, crypto_amount, from_address, to_address, remark=""):
#     try:
#         deposite_request = DepositeRequest(
#             user_id=user_id,
#             crypto_name=crypto_name,
#             crypto_amount=crypto_amount,
#             from_address=from_address,
#             to_address=to_address,
#             remark=remark,
#             status="Pending"
#         )
#         deposite_request.save()
#         payload = {
#             "success": True,
#             "deposite_request": deposite_request.to_dict()
#         }
#     except Exception as e:
#         payload = {
#             "success": False,
#             "errors": [f"Graph QL Error : {e}"]
#         }
#     return payload


# # Create Deposite Request
# def resolve_create_deposit_request(obj, info, user_id, crypto_name, crypto_amount, from_address, to_address, remark=""):
#     try:
#         deposite_request = DepositeRequest(
#             user_id=user_id,
#             crypto_name=crypto_name,
#             crypto_amount=crypto_amount,
#             from_address=from_address,
#             to_address=to_address,
#             remark=remark,
#             status="Pending"
#         )
#         deposite_request.save()
#         payload = {
#             "success": True,
#             "deposite_request": deposite_request.to_dict()
#         }
#     except Exception as e:
#         payload = {
#             "success": False,
#             "errors": [f"Graph QL Error : {e}"]
#         }
#     return payload
