# -*- coding: utf-8 -*-
# core.urls
# 

# Following few lines is an example urlmapping with an older interface.
"""
from werkzeug.routing import EndpointPrefix, Rule

def make_rules():
  return [
    EndpointPrefix('core/', [
      Rule('/', endpoint='index'),
    ]),
  ]

all_views = {
  'core/index': 'core.views.index',
}
"""

from kay.routing import (
  ViewGroup, Rule
)

view_groups = [
  ViewGroup(
    Rule('/', endpoint='index', view='core.views.index'),
    Rule('/notebooks', endpoint='notebooks', view='core.views.notebooks'),
    Rule('/new_notebook', endpoint='new_notebook', view='core.views.new_notebook'),
    Rule('/update_notebook', endpoint='update_notebook', view='core.views.update_notebook'),
    Rule('/delete_notebook', endpoint='delete_notebook', view='core.views.delete_notebook'),
    Rule('/receipt', endpoint='receipt', view='core.views.receipt'),
    Rule('/list_ref_place', endpoint='list_ref_place', view='core.views.list_ref_place'),
    Rule('/income', endpoint='income', view='core.views.income'),
    Rule('/list_ref_source', endpoint='list_ref_source', view='core.views.list_ref_source'),
    Rule('/report', endpoint='report', view='core.views.report'),
    Rule('/item', endpoint='item', view='core.views.item'),
    Rule('/list_ref_category', endpoint='list_ref_category', view='core.views.list_ref_category'),
    Rule('/profile', endpoint='profile', view='core.views.profile'),
    Rule('/add_profile', endpoint='add_profile', view='core.views.add_profile'),
    Rule('/update_profile', endpoint='add_profile', view='core.views.add_profile'),
    Rule('/<nickname>', endpoint='wall', view='core.views.wall'),
    Rule('/wall-logoin', endpoint='wall-login', view='core.views.wall'),
  )
]

