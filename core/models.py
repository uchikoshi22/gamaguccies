# -*- coding: utf-8 -*-
# core.models

from google.appengine.ext import db
from kay.auth.models import GoogleUser
import kay.db

class MyUser(GoogleUser):
  pass

class Profile(db.Model):
  owner = kay.db.OwnerProperty()
  nickname = db.StringProperty()
  managers = db.StringListProperty()

class Source(db.Model):
  owner = kay.db.OwnerProperty()
  sources = db.StringListProperty()

class Place(db.Model):
  owner = kay.db.OwnerProperty()
  places = db.StringListProperty()

class Category(db.Model):
  owner = kay.db.OwnerProperty()
  categories = db.StringListProperty()

class Notebook(db.Model):
  owner = kay.db.OwnerProperty()
  seq = db.IntegerProperty()
  name = db.StringProperty()
  in_goal = db.IntegerProperty()
  out_goal = db.IntegerProperty()
  memo = db.TextProperty()
  is_main = db.BooleanProperty()
  is_itemized = db.BooleanProperty()
  created = db.DateTimeProperty(auto_now_add=True)


class Income(db.Model):
  owner = kay.db.OwnerProperty()
  seq = db.IntegerProperty()
  date = db.DateProperty()
  amount = db.IntegerProperty()
  source = db.StringProperty()
  memo = db.TextProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  notebook = db.ReferenceProperty(Notebook)

class Receipt(db.Model):
  owner = kay.db.OwnerProperty()
  date = db.DateProperty()
  seq = db.IntegerProperty()
  sum = db.IntegerProperty()
  memo = db.TextProperty()
  place = db.StringProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  notebook = db.ReferenceProperty(Notebook)

class Item(db.Model):
  owner = kay.db.OwnerProperty()
  seq = db.IntegerProperty()
  name = db.StringProperty()
  unit_price = db.IntegerProperty()
  number = db.IntegerProperty()
  subtotal = db.IntegerProperty()
  memo = db.TextProperty()
  category = db.StringProperty()
  receipt = db.ReferenceProperty(Receipt)

