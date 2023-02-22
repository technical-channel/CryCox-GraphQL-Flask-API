# from main import db
from mongoengine import Document
from mongoengine.fields import (
    StringField, DateTimeField, BooleanField, IntField, ObjectIdField, FloatField, ListField)
import json
import datetime
from bson.objectid import ObjectId


class Registration(Document):
    meta = {'collection': 'registration'}
    username = StringField()
    email = StringField()
    phone = StringField()
    metamask = StringField()
    password = StringField(required=True)
    createdAt = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "metamask": self.metamask,
            "password": self.password,
            "createdAt": self.createdAt
        }


class UserInfo(Document):
    meta = {'collection': 'userinfo'}
    user_id = ObjectIdField(required=True)
    username = StringField(required=True)
    preferred_currency = StringField(default=None)
    language = StringField(default=None)
    bio = StringField(default=None)
    image = StringField(default=None)
    is_email_verified = BooleanField(default=False)
    is_number_verified = BooleanField(default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "preferred_currency": self.preferred_currency,
            "language": self.language,
            "bio": self.bio,
            "image": self.image,
            "is_email_verified": self.is_email_verified,
            "is_number_verified": self.is_number_verified
        }


class Trade(Document):
    meta = {'collection': 'trade'}
    buyer_id = ObjectIdField()
    seller_id = ObjectIdField()
    offer_id = ObjectIdField()
    cryptocurrency = StringField(required=True)
    crypto_trade_amount = FloatField()
    fiat_trade_amount = FloatField(default=0)
    trade_rate = FloatField()
    date_start_time = DateTimeField(default=datetime.datetime.now)
    trade_time = IntField()
    trade_type = StringField()
    trade_outcome = StringField()
    pay_via = StringField()
    buyer_feedback = IntField(min_value=1, max_value=5)
    seller_feedback = IntField(min_value=1, max_value=5)
    buyer_feedback_text = StringField()
    seller_feedback_text = StringField()
    buyer_paid = BooleanField(default=False)
    seller_released = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "offer_id": self.offer_id,
            "cryptocurrency": self.cryptocurrency,
            "crypto_trade_amount": self.crypto_trade_amount,
            "fiat_trade_amount": self.fiat_trade_amount,
            "trade_rate": self.trade_rate,
            "date_start_time": self.date_start_time,
            "trade_time": self.trade_time,
            "trade_type": self.trade_type,
            "trade_outcome": self.trade_outcome,
            "pay_via": self.pay_via,
            "buyer_feedback": self.buyer_feedback,
            "seller_feedback": self.seller_feedback,
            "buyer_feedback_text": self.buyer_feedback_text,
            "seller_feedback_text": self.seller_feedback_text,
            "buyer_paid": self.buyer_paid,
            "seller_released": self.seller_released,
            "created_at": self.created_at
        }


class CreateOffer(Document):
    meta = {'collection': 'offer'}
    user_id = ObjectIdField()
    crypto_name = StringField(required=True)
    price_type = StringField(required=True)
    offer_type = StringField(required=True)
    payment_type = ListField(required=True)
    preferred_currency = StringField(required=True)
    offer_tags = ListField()
    offerer_verified = BooleanField(default=False)
    min_purchase = FloatField()
    max_purchase = FloatField()
    offer_price = FloatField()
    offer_margin = IntField()
    offer_time_minute = IntField(default=30)
    offer_label = StringField()
    offer_terms = StringField()
    offer_condition = StringField()
    offer_location = StringField()
    offer_owner_location = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "crypto_name": self.crypto_name,
            "price_type": self.price_type,
            "offer_type": self.offer_type,
            "payment_type": self.payment_type,
            "preferred_currency": self.preferred_currency,
            "offer_tags": self.offer_tags,
            "offerer_verified": self.offerer_verified,
            "min_purchase": self.min_purchase,
            "max_purchase": self.max_purchase,
            "offer_price": self.offer_price,
            "offer_margin": self.offer_margin,
            "offer_time_minute": self.offer_time_minute,
            "offer_label": self.offer_label,
            "offer_terms": self.offer_terms,
            "offer_condition": self.offer_condition,
            "offer_location": self.offer_location,
            "offer_owner_location": self.offer_owner_location,
            "created_at": self.created_at
        }


class Assets(Document):
    meta = {'collection': 'assets'}
    user_id = ObjectIdField(default=0)
    btc = FloatField(default=0)
    eth = FloatField(default=0)
    bnb = FloatField(default=0)
    shiba = FloatField(default=0)
    doge = FloatField(default=0)
    usdt_eth = FloatField(default=0)
    usdt_bnb = FloatField(default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "btc": self.btc,
            "eth": self.eth,
            "bnb": self.bnb,
            "shiba": self.shiba,
            "doge": self.doge,
            "usdt_eth": self.usdt_eth,
            "usdt_bnb": self.usdt_bnb
        }


class DepositeAssets(Document):
    meta = {'collection': 'deposite'}
    user_id = ObjectIdField()
    assets_name = StringField()
    assets_amount = FloatField()
    deposite_time = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assets_name": self.assets_name,
            "assets_amount": self.assets_amount,
            "deposite_time": self.deposite_time
        }


class OTP(Document):
    meta = {'collection': 'otp'}
    email = StringField(required=True)
    otp = StringField()
    updated_at = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "otp": self.otp,
            "updated_at": self.updated_at
        }


class Test(Document):
    meta = {'collection': 'test'}
    public_id = StringField()
    name = StringField()
    email = StringField()
    password = StringField()

    def to_dict(self):
        return {
            "id": self.id,
            "public_id": self.public_id,
            "name": self.name,
            "email": self.email,
            "password": self.password
        }


class DepositeRequest(Document):
    meta = {'collection': 'desposite_request'}
    user_id = ObjectIdField()
    crypto_name = StringField()
    crypto_amount = FloatField()
    from_address = StringField()
    to_address = StringField()
    remark = StringField()
    status = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "crypto_name": self.crypto_name,
            "crypto_amount": self.crypto_amount,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "remark": self.remark,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
