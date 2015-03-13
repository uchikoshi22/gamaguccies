# -*- coding: utf-8 -*-
"""
core.views
"""

import sys
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout

from werkzeug import (
  unescape, redirect, Response,
)
from werkzeug.exceptions import (
  NotFound, MethodNotAllowed, BadRequest
)

from kay.utils import (
  render_to_response, reverse,
  get_by_key_name_or_404, get_by_id_or_404,
  to_utc, to_local_timezone, url_for, raise_on_dev
)

from kay.auth.decorators import login_required

from core.models import *
from core.forms import *

from time import time
from datetime import date
from calendar import monthrange

NOTEBOOK_LIMIT = int(10)

@login_required
def report(request):
  owner = request.user
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
      
  key = request.values.get('key')
  notebook = Notebook.get_by_id(int(key))
  year = date.today().year
  month = date.today().month
  day = date.today().day
  bom = date(year, month, 1)
  eom = date(year, month, int(monthrange(year, month)[1]))
  incomes = Income.gql("WHERE owner=:1 AND date >=:2 AND date <=:3 AND notebook=:4",
                       owner, bom, eom, notebook)
  receipts = Receipt.gql("WHERE owner=:1 AND date >=:2 AND date <=:3 AND notebook=:4",
                         owner, bom, eom, notebook)


  income_sum = 0
  receipt_sum = 0

  for income in incomes:
    income_sum += income.amount

  for receipt in receipts:
    receipt_sum += receipt.sum

  in_goal = notebook.in_goal
  out_goal = notebook.out_goal

  #income_ave = income_sum / day
  receipt_ave = receipt_sum / day
  receipt_target = out_goal / int(monthrange(year, month)[1])
  receipt_forecast = receipt_ave * int(monthrange(year, month)[1])

  income_diff = in_goal - income_sum
  receipt_diff = out_goal - receipt_sum


  
  return render_to_response('core/report.html',
                            {"key": key,
                             "notebook": notebook,
                             "notebooks": notebooks,
                             "notebook_counter": notebook_counter,
                             "income_sum": income_sum,
                             "NOTEBOOK_LIMIT": NOTEBOOK_LIMIT,
                             "receipt_sum": receipt_sum,
                             "in_goal": in_goal,
                             "out_goal": out_goal,
                             #"income_ave": income_ave,
                             "receipt_target": receipt_target,
                             "receipt_ave": receipt_ave,
                             "receipt_forecast": receipt_forecast,
                             "income_diff": income_diff,
                             "receipt_diff": receipt_diff,
                             })


@login_required
def list_ref_source(request):
  owner = request.user
  sources = Source.gql("WHERE owner=:1", owner)
  if sources.count() > 0:
    source_list = sources[0]
  else:
    source_list = "a"
  return render_to_response('core/list_ref_source.html',
                            {"source_list": source_list,
                             })

@login_required
def income(request):
  owner = request.user
  today = date.today()
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
  form = IncomeForm()
  if request.method == "POST" and form.validate(request.form):
    income = Income()
    income.owner = owner
    income.date = form['date']
    income.seq = int(time())
    income.amount = form['amount']
    income.memo = form['memo']
    key = request.values.get('key')
    income.notebook = Notebook.get_by_id(int(key))
    income.source = form['source']

    source_lists = Source.gql("WHERE owner=:1", owner)
    if source_lists.count() > 0:
      source_list = source_lists[0]
      if is_source_duplex(income.source, source_list.sources):
        pass
      else:
        source_list.sources += income.source.split(",")
        source_list.put()
    else:
      source_list = Source()
      source_list.owner = owner
      source_list.sources = income.source.split(",")
      source_list.put()

    income.put()
    redirect_url = '/income?key=' + key
    return redirect(redirect_url)
    
  else:
    if notebook_counter == 0:
      return redirect('/notebooks')
    else:
      if request.values.get('key'):
        key = request.values.get('key')
        notebook = Notebook.get_by_id(int(key))
      else:
        default_notebooks = Notebook.gql("WHERE owner=:1 AND is_main=:2",
                                         owner, True)
        notebook = default_notebooks[0]

      return render_to_response('core/income.html',
                                {'notebook_counter': notebook_counter,
                                 'notebooks': notebooks,
                                 'NOTEBOOK_LIMIT': NOTEBOOK_LIMIT,
                                 'notebook': notebook,
                                 'form': form.as_widget(),
                                 'today': today,
                                 })

@login_required
def list_ref_category(request):
  owner = request.user
  categories = Category.gql("WHERE owner=:1", owner)
  if categories.count() > 0:
    category_list = categories[0]
  else:
    category_list = None
  return render_to_response('core/list_ref_category.html',
                            {"category_list": category_list,
                             })
                  


@login_required
def item(request):
  owner = request.user
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
  key = request.values.get('key')
  receipt = Receipt.get_by_id(int(key))
  items = Item.gql("WHERE receipt=:1", receipt)
  if items.count() == 0:
    items = None
  categories = Category.gql("WHERE owner=:1", owner)
  notebook = receipt.notebook
  form = ItemForm()
  
  if request.method == "POST" and form.validate(request.form):
    item =Item()
    item.owner = owner
    item.seq = int(time())
    item.name = form['name']
    item.unit_price = form['unit_price']
    item.number = form['number']
    item.subtotal = form['subtotal']
    item.memo = form['memo']
    item.receipt = receipt
    item.category = form['category']

    category_lists = Category.gql("WHERE owner=:1", owner)
    if category_lists.count() > 0:
      category_list = category_lists[0]
      if is_category_duplex(item.category, category_list.categories):
        pass
      else:
        category_list.categories += item.category.split(",")
        category_list.put()
    else:
      category_list = Category()
      category_list.owner = owner
      category_list.categories = item.category.split(",")
      category_list.put()

    item.put()
    redirect_url = '/item?key=' + key
    return redirect(redirect_url)
    
  else:
    return render_to_response('core/item.html',
                            {'notebook_counter': notebook_counter,
                             'notebooks': notebooks,
                             'notebook': notebook,
                             'receipt': receipt,
                             'categories': categories,
                             'NOTEBOOK_LIMIT': NOTEBOOK_LIMIT,
                             'items': items,
                             'form': form.as_widget(),
                             })
      


@login_required
def list_ref_place(request):
  owner = request.user
  places = Place.gql("WHERE owner=:1", owner)
  if places.count() > 0:
    place_list = places[0]
  else:
    place_list = None
  return render_to_response('core/list_ref_place.html',
                            {"place_list": place_list,
                              })


@login_required
def receipt(request):
  owner = request.user
  today = date.today()
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
  form = ReceiptForm()

  if request.method == "POST" and form.validate(request.form):
    receipt = Receipt()
    receipt.owner = owner
    receipt.date = form['date']
    receipt.seq = int(time())
    receipt.sum = form['sum']
    receipt.memo = form['memo']
    key = request.values.get('key')
    receipt.notebook = Notebook.get_by_id(int(key))
    receipt.place = form['place']

    place_lists = Place.gql("WHERE owner=:1", owner)
    if place_lists.count() > 0:
      place_list = place_lists[0]
      if is_place_duplex(receipt.place, place_list.places):
        pass
      else:
        place_list.places += receipt.place.split(",")
        place_list.put()
    else:
      place_list = Place()
      place_list.owner = owner
      place_list.places = receipt.place.split(",")
      place_list.put()

    receipt.put()

    if receipt.notebook.is_itemized:
      redirect_url = '/item?key=' + str(receipt.key().id())
      return redirect(redirect_url)
    else:
      redirect_url = '/receipt?key=' + key
      return redirect(redirect_url)
    
  else:
    if notebook_counter == 0:
      return redirect('/notebooks')
    else:
      if request.values.get('key'):
        key = request.values.get('key')
        notebook = Notebook.get_by_id(int(key))
      else:
        default_notebooks = Notebook.gql("WHERE owner=:1 AND is_main=:2",
                                         owner, True)
        notebook = default_notebooks[0]
  
      return render_to_response('core/receipt.html',
                                {'notebook_counter': notebook_counter,
                                 'notebooks': notebooks,
                                 'NOTEBOOK_LIMIT': NOTEBOOK_LIMIT,
                                 'notebook': notebook,
                                 'form': form.as_widget(),
                                 'today': today,
                                 })



# Notebook Class of models.py
@login_required
def delete_notebook(request):
  owner = request.user
  key = request.values.get('key')
  if request.method == "GET":
    notebook = Notebook.get_by_id(int(key))
    if notebook.is_main:
      make_oldest_main(owner)
    notebook.delete()
  return redirect(url_for('core/notebooks'))

@login_required
def update_notebook(request):
  owner = request.user
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
  key = request.values.get('key')
  notebook = Notebook.get_by_id(int(key))
  form = NotebookForm({'name': notebook.name,
                       'in_goal': notebook.in_goal,
                       'out_goal': notebook.out_goal,
                       'is_main':notebook.is_main,
                       'is_itemized': notebook.is_itemized,
                       'memo': notebook.memo,
                       })

  if request.method == "GET":
    return render_to_response('core/update_notebook.html',
                              {'form': form.as_widget(),
                               'notebooks': notebooks,
                               'NOTEBOOK_LIMIT': NOTEBOOK_LIMIT,
                               'notebook_counter': notebook_counter,
                               })

  if request.method == "POST" and form.validate(request.form):
    notebook.name = form['name']
    notebook.in_goal = form['in_goal']
    notebook.out_goal = form['out_goal']
    notebook.memo = form['memo']
    notebook.is_main = form['is_main']
    notebook.is_itemized = form['is_itemized']
    notebook.put()
    return redirect(url_for('core/notebooks'))


@login_required
def new_notebook(request):
  owner = request.user
  form = NotebookForm()
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
  if request.method == "POST" and form.validate(request.form):
    notebook = Notebook()
    notebook.owner = owner
    notebook.name = form['name']
    notebook.in_goal = set_zero_yen(form['in_goal'])
    notebook.out_goal = set_zero_yen(form['out_goal'])
    notebook.memo = form['memo']
    notebook.is_main = form['is_main']
    if notebook.is_main:
      change_prev_main(owner)
    if not notebook_counter:
      notebook.is_main = True
    notebook.is_itemized = form['is_itemized']
    notebook.put()
    return redirect(url_for('core/notebooks'))
    
  else:
    return render_to_response('core/new_notebook.html',
                              {'form': form.as_widget(),
                               'notebooks': notebooks,
                               'notebook_counter': notebook_counter,
                               'NOTEBOOK_LIMIT': NOTEBOOK_LIMIT,
                                })


@login_required
def notebooks(request):
  owner = request.user
  notebooks = Notebook.gql("WHERE owner=:1 ORDER BY seq", owner)
  notebook_counter = notebooks.count()
  return render_to_response('core/notebooks.html',
                            {'notebooks': notebooks,
                             'notebook_counter': notebook_counter,
                             'NOTEBOOK_LIMIT': NOTEBOOK_LIMIT,
                              })


def wall(request, nickname):
  if request.method == "POST":
    email = request.values.get('email')
    profiles = Profile.gql("WHERE nickname=:1", nickname)

    profile = profiles[0]
    owner = profile.owner

    if email in profile.managers:
      is_manager = True
    else:
      is_manager = False
    return render_to_response('core/wall.html',
                              {'nickname': nickname,
                               'email': email,
                               'owner': owner,
                               'profiles': profile,
                               'is_manager': is_manager,
                               })
  else:
    return render_to_response('core/wall_login.html',
                              {'nickname': nickname,
                               })


@login_required
def update_profile(request):
  owner = request.user
  form = ProfileForm()
  if request.method == "POST" and form.validate(request.form):
    profile = Profile()
    profile.owner = owner
    profile.nickname = form['nickname']
    manager1 = request.values.get('manager1')
    manager2 = request.values.get('manager2')
    manager3 = request.values.get('manager3')
    manager4 = request.values.get('manager4')
    manager5 = request.values.get('manager5')
    
    managers = []
    if not manager1 == "":
      managers.append(manager1)
    if not manager2 == "":
      managers.append(manager2)
    if not manager3 == "":
      managers.append(manager3)
    if not manager4 == "":
      managers.append(manager4)
    if not manager5 == "":
      managers.append(manager5)

    profile.managers = managers
    profile.put()
    return redirect('/profile')
  else:
    return redirect('/profile')
  

@login_required
def add_profile(request):
  owner = request.user
  form = ProfileForm()
  if request.method == "POST" and form.validate(request.form):
    profile = Profile()
    profile.owner = owner
    profile.nickname = form['nickname']
    manager1 = request.values.get('manager1')
    manager2 = request.values.get('manager2')
    manager3 = request.values.get('manager3')
    manager4 = request.values.get('manager4')
    manager5 = request.values.get('manager5')
    
    managers = []
    if not manager1 == "":
      managers.append(manager1)
    if not manager2 == "":
      managers.append(manager2)
    if not manager3 == "":
      managers.append(manager3)
    if not manager4 == "":
      managers.append(manager4)
    if not manager5 == "":
      managers.append(manager5)

    profile.managers = managers
    profile.put()
    return redirect('/profile')
    
  else:
    profile = Profile.gql("WHERE owner=:1", owner)
    if profile.count() >= 1:
      return redirect('/profile')
    else:
      return render_to_response('core/add_profile.html',
                                {'form': form.as_widget(),
                                  })

@login_required
def profile(request):
  owner = request.user
  profiles = Profile.gql("WHERE owner=:1", owner)
  if profiles.count() < 1:
    profile = None
    form = ProfileForm()
  else:
    profile = profiles[0]
    form = ProfileForm(initial={"nickname": profile.nickname})
    
  return render_to_response('core/profile.html',
                            {'owner': owner,
                             'profile': profile,
                             'form': form.as_widget(),
                             })


@login_required
def index(request):
  owner = request.user
  profile = Profile.gql("WHERE owner=:1", owner)
  if profile.count() < 1:
    profile = None
  return render_to_response('core/index.html',
                            {'owner': owner,
                             'profile': profile,
                             })


# Common function
def change_prev_main(owner):
  notebooks = Notebook.gql("WHERE owner=:1 AND is_main=TRUE", owner)
  try:
    prev_main = notebooks.get()
    prev_main.is_main = False
    prev_main.put()
  except:
    pass


def make_oldest_main(owner):
  notebooks = Notebook.gql("WHERE owner=:1", owner)
  notebook = notebooks[0]
  notebook.is_main = True
  notebook.put()

def set_zero_yen(yen):
  if yen == None:
    return 0
  else:
    return yen

def is_place_duplex(place, place_list):
  if place in place_list:
    return True
  else:
    return False

def is_source_duplex(source, source_list):
  if source in source_list:
    return True
  else:
    return False

def is_category_duplex(category, category_list):
  if category in category_list:
    return True
  else:
    return False
