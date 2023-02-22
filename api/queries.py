from datetime import datetime
from ariadne import convert_kwargs_to_snake_case
from mongoengine import ObjectIdField
# from .models import Todo, Registration, UserInfo, CreateOffer, Trade
from api.models import Registration, UserInfo, Trade, CreateOffer, DepositeAssets, Assets, OTP
import requests
import os
from twilio.rest import Client
from mongoengine.queryset.visitor import Q
from flask import session


phone_number = os.getenv("MYPHONENUMBER")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_sid = os.getenv("TWILIO_VERIFY_SID")


def resolve_check_email_otp(obj, info, to_email, otp):
    try:
        user = OTP.objects(email__iexact=to_email, otp=otp).first()
        if user:
            print("User has somethings")
            last_otp_time = int(user.updated_at.timestamp())
            current_time = int(datetime.now().timestamp())
            print(current_time, last_otp_time)
            if current_time <= last_otp_time + 60:
                payload = {
                    "success": True,
                    "status": ["approved"],
                }
                print("approved")
            else:
                payload = {
                    "success": False,
                    "status": ["expire"],
                }
                print("expire")
        else:
            payload = {
                "success": False,
                "status": ["failed"],
            }
        return payload
    except Exception as e:
        payload = {
            "success": False,
            "status": ["pending"],
            "errors": [f"Graph QL Error : {e}"]
        }
        return payload


# register metamask address for the user
def resolve_check_metamask(obj, info, metamask):
    try:
        user = Registration.objects(metamask=metamask).first()
        if user:
            payload = {
                "success": True,
                "user": [user.to_dict()]
            }
        else:
            payload = {
                "success": False,
                "errors": [f"Metamask id '{metamask}' not Register"]
            }
        return payload
    except Exception as e:  # trade not found
        payload = {
            "success": False,
            "errors": [f"Graph QL Error : {e}"]
        }
    return payload


def resolve_depositeHistory_by_UserId(obj, info, user_id):
    try:
        depositeAssets = DepositeAssets.objects(user_id=user_id)
        payload = {
            "success": True,
            "deposite": [x.to_dict() for x in depositeAssets]
        }
    except:
        payload = {
            "success": False,
            "errors": [f"User matching id {user_id} not found or Internal Server Error"]
        }

    return payload

    # API-12 Trade By User Id


def resolve_trade_by_userId(obj, info, user_id, cryptocurrency="", trade_type="", trade_outcome="", start_date="", end_date="", pay_via=""):
    try:

        query = {}

        if cryptocurrency != "":
            query["cryptocurrency"] = cryptocurrency.lower()
        if trade_type != "":
            query["trade_type"] = trade_type.lower()
        if trade_outcome != "":
            query["trade_outcome"] = trade_outcome.lower()
        if pay_via != "":
            query["pay_via"] = pay_via.lower()

        print("query : ", query)

        if (start_date == "") or (end_date == ""):
            trades = Trade.objects((Q(buyer_id=user_id) |
                                    Q(seller_id=user_id)) & Q(__raw__=query))
            all_trades = [trade.to_dict() for trade in trades]
            payload = {
                "success": True,
                "trade": all_trades
            }
        else:
            trades = Trade.objects((Q(buyer_id=user_id) |
                                    Q(seller_id=user_id)) & Q(__raw__=query) &
                                   (Q(date_start_time__gte=datetime.strptime(start_date, '%d-%m-%Y').date()) &
                                   Q(date_start_time__lte=datetime.strptime(end_date, '%d-%m-%Y').date())))
            all_trades = [trade.to_dict() for trade in trades]
            payload = {
                "success": True,
                "trade": all_trades
            }

        # start = "01-01-2022"

        # end = "01-03-2025"
        # startTime = datetime.strptime(start, '%d-%m-%Y').date()
        # endTime = datetime.strptime(end, '%d-%m-%Y').date()
        # data = Trade.objects(Q(date_start_time__gte=startTime)
        #                      & Q(date_start_time__lte=endTime))
        # data

    except:
        payload = {
            "success": False,
            "errors": [f"Offer matching id {user_id} not found, Internal Server Error"]
        }
    return payload


# API-13.  Offer by user id (Filter )
def resolve_offer_by_userId(obj, info, user_id, offer_type="", crypto_name=""):
    try:
        if offer_type == "" and crypto_name == "":
            offers = CreateOffer.objects(user_id=user_id)
        else:
            if offer_type != "":
                offers = CreateOffer.objects(
                    user_id=user_id, offer_type=offer_type.lower())
            if crypto_name != "":
                offers = CreateOffer.objects(
                    user_id=user_id, crypto_name=crypto_name.lower())
            if offer_type != "" and crypto_name != "":
                offers = CreateOffer.objects(
                    user_id=user_id, crypto_name=crypto_name.lower(), offer_type=offer_type.lower())

        all_offers = [offer.to_dict() for offer in offers]
        payload = {
            "success": True,
            "offer": all_offers
        }

    except AttributeError:  # trade not found
        payload = {
            "success": False,
            "errors": [f"Offer matching id {id} not found"]
        }
    return payload


# Trade by trade id
def resolve_trade_by_trade_id(obj, info, id):
    try:
        trade = Trade.objects.with_id(id)
        payload = {
            "success": True,
            "trade": [trade.to_dict()]
        }

    except AttributeError:  # trade not found
        payload = {
            "success": False,
            "errors": [f"Trade matching id {id} not found"]
        }

    return payload


# API-16 Fetch User Balance by user id
def resolve_userBalance_by_id(obj, info, user_id):
    try:
        balance = Assets.objects(user_id=user_id)
        payload = {
            "success": True,
            "balance": balance[0].to_dict()
        }

    except:
        payload = {
            "success": False,
            "errors": [f"User matching id {user_id} not found or Internal Server Error"]
        }

    return payload


# API-6 - Live price
def resolve_getLivePrice(obj, info, symbol, currency):
    try:
        # print("Symbol and Currency : ", symbol, currency)
        # if symbol != "USDT":
        #     cryptoApi = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        #     r = requests.get(cryptoApi)
        #     btc_usdt_price = r.json()['price']
        # else:
        #     btc_usdt_price = 1
        # currencyApi = "https://api.exchangerate.host/latest?/source=ecb&base=USD"
        # r = requests.get(currencyApi)
        # inrPrice = r.json()['rates'][currency]
        # data = inrPrice * float(btc_usdt_price)
        url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms={currency}"
        r = requests.get(url)
        data = r.json()[str(currency.upper())]
        payload = {
            "success": True,
            "data": [data]
        }

    except:  # todo not found
        payload = {
            "success": False,
            "errors": ["Invalid Input Arguments"]
        }

    return payload


# API-5 - All Offers (filter)
def resolve_all_offers(obj, info, offer_type="", crypto_name="", payment_type=[],
                       preferred_currency="", offer_location="", offer_owner_location="",
                       offerer_verified=False, want_to_spend=0):
    try:
        q = {}
        if offer_type.strip() != "":
            q["offer_type"] = offer_type.lower()
        if crypto_name.strip() != "":
            q["crypto_name"] = crypto_name.lower()
        # if payment_type != "":
        #     q["payment_type"] = payment_type.lower()
        if preferred_currency.strip() != "":
            q["preferred_currency"] = preferred_currency.lower()
        if offer_location.strip() != "":
            q["offer_location"] = offer_location.lower()
        if offer_owner_location.strip() != "":
            q["offer_owner_location"] = offer_owner_location.lower()
        q["offerer_verified"] = offerer_verified

        print("EDDDDDDDD")

        if len(payment_type) == 0:
            if want_to_spend > 0:

                offers = CreateOffer.objects(
                    Q(__raw__=q) & Q(min_purchase__lte=want_to_spend) & Q(max_purchase__gte=want_to_spend))
                all_offers = [offer.to_dict() for offer in offers]
                print("all_offers 1 : ", all_offers)
                payload = {
                    "success": True,
                    "offer": all_offers
                }
            else:
                offers = CreateOffer.objects(__raw__=q)
                all_offers = [offer.to_dict() for offer in offers]
                print("all_offers 2 : ", all_offers, q)
                payload = {
                    "success": True,
                    "offer": all_offers
                }
            return payload
        else:
            payment_type = [x.lower() for x in payment_type]
            if want_to_spend > 0:
                print("EDDDDDDDD23", payment_type[0].lower())
                offers = CreateOffer.objects(
                    Q(__raw__=q) & Q(min_purchase__lte=want_to_spend) & Q(max_purchase__gte=want_to_spend) & Q(payment_type__in=payment_type))
                all_offers = [offer.to_dict() for offer in offers]
                print("all_offers 3 : ", all_offers)
                payload = {
                    "success": True,
                    "offer": all_offers
                }
                return payload
            else:
                offers = CreateOffer.objects(Q(__raw__=q) & Q(
                    payment_type__in=payment_type))
                all_offers = [offer.to_dict() for offer in offers]
                print("all_offers 4 : ", all_offers,
                      q, payment_type)
                payload = {
                    "success": True,
                    "offer": all_offers
                }
                return payload

    except Exception as e:
        payload = {
            "success": False,
            "errors": [f"Internal Servar Error : {e}"]
        }
    return payload


# API-6 Offer By Id
def resolve_offer_by_id(obj, info, offer_id):
    try:
        offer = CreateOffer.objects.with_id(offer_id)
        payload = {
            "success": True,
            "offer": [offer]
        }

    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": [f"Offer matching id {offer_id} not found"]
        }

    return payload


# API-9 User info By user Id
def resolve_userinfo_by_id(obj, info, user_id):
    try:
        user = UserInfo.objects(user_id=user_id)
        payload = {
            "success": True,
            "info": user[0].to_dict()
        }

    except:  # todo not found
        payload = {
            "success": False,
            "errors": [f"User matching id {user_id} not found"]
        }

    return payload


def resolve_user(obj, info, id):
    print("id : ", id, "Resolve_user is jsut called")
    try:
        user = Registration.objects.with_id(id)
        payload = {
            "success": True,
            "user": user.to_dict()
        }

    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": [f"User matching id {id} not found"]
        }

    return payload


def resolve_userInfo(obj, info, id):
    print("id : ", id, "Resolve_user is jsut called")
    try:
        userInfo = UserInfo.objects.with_id(id)
        payload = {
            "success": True,
            "UserInfo": userInfo.to_dict()
        }

    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": [f"User Info matching id {id} not found"]
        }

    return payload


# Trade by offer id
# API-8 Feedbac by Trade id
def resolve_trade_by_offer_id(obj, info, offer_id):
    try:
        trades = Trade.objects(offer_id=offer_id)
        all_trades = [trade.to_dict() for trade in trades]
        payload = {
            "success": True,
            "trade": all_trades
        }

    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": [f"Offer matching id {offer_id} not found in Trade Data"]
        }

    return payload


# def resolve_todos(obj, info):
#     try:
#         todos = [todo.to_dict() for todo in Todo.objects.all()]
#         payload = {
#             "success": True,
#             "todos": todos
#         }
#     except Exception as error:
#         payload = {
#             "success": False,
#             "errors": [str(error)]
#         }
#     return payload


#
# def resolve_todo(obj, info, id):
#     try:
#         todo=Todo.objects.with_id(id)
#         payload = {
#             "success": True,
#             "todo": todo.to_dict()
#         }

#     except AttributeError:  # todo not found
#         payload = {
#             "success": False,
#             "errors": [f"Todo matching id {id} not found"]
#         }

#     return payload

# def filterOffers(**kwargs):
#     final_data = []
#     for dataObj in CreateOffer.objects.all():
#         right = False
#         for i in kwargs.keys():
#             if kwargs[i] != "":
#                 if kwargs[i] == dataObj[i]:
#                     right = True
#         if right:
#             final_data.append(dataObj)
#     return final_data


# def resolve_verify_otp(obj, info, id, otp):
#     try:
#         verifyTwilioOTP(otp)
#         payload = {
#             "success": True,
#             "message": [f"OTP Verify sucessfully"]
#         }
#         return payload

#     except AttributeError as error:
#         payload = {
#             "success": False,
#             "errors":  [f"User matching id {id} was not found, or wrong input parameters"]
#         }

#         return payload


def verifyTwilioOTP(otp):
    client = Client(account_sid, auth_token)
    verification_check = client.verify \
                               .v2 \
                               .services(verify_sid) \
                               .verification_checks \
                               .create(to="+918955562054", code=otp)
    print(verification_check.status)


# def findOffer(offer_type, crypto_name, payment_type, preferred_currency, want_to_spend, offer_location, offer_owner_location, offerer_verified):
#     data = CreateOffer.objects(offer_type=offer_type, crypto_name=crypto_name, payment_type=payment_type,
#                                offer_location=offer_location, preferred_currency=preferred_currency, offer_owner_location=offer_owner_location, offerer_verified=offerer_verified)
#     offers = []
#     for x in data:
#         if (data[0].to_dict()["min_purchase"] <= want_to_spend) and (data[0].to_dict()["max_purchase"] >= want_to_spend):
#             offers.append(x)
#     return offers


def filterOffers(offer_type, crypto_name, payment_type, want_to_spend, offer_location, offer_owner_location, preferred_currency, offerer_verified):

    offersList = CreateOffer.objects(offer_type=offer_type, crypto_name=crypto_name, payment_type=payment_type,
                                     offer_location=offer_location, offer_owner_location=offer_owner_location, preferred_currency=preferred_currency, offerer_verified=offerer_verified)
    offers = []
    for offer in offersList:
        currentOffer = offer.to_dict()
        if (want_to_spend >= currentOffer['min_purchase']) and (want_to_spend <= currentOffer['max_purchase']):
            offers.append(offer)
    return offers
