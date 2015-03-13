# -*- coding: utf-8 -*-
# admin.urls
# 

# Following few lines is an example urlmapping with an older interface.
"""
from werkzeug.routing import EndpointPrefix, Rule

def make_rules():
  return [
    EndpointPrefix('admin/', [
      Rule('/', endpoint='index'),
    ]),
  ]

all_views = {
  'admin/index': 'admin.views.index',
}
"""

from kay.routing import (
  ViewGroup, Rule
)

view_groups = [
  ViewGroup(
    Rule('/', endpoint='index', view='admin.views.index'),
  )
]

