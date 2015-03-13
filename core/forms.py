# -*- coding: utf-8 -*-

from kay.utils import forms
from kay.utils.validators import ValidationError
from core.models import *
from google.appengine.ext import db


class ItemForm(forms.Form):
  name = forms.TextField(label=u"商品名")
  unit_price = forms.IntegerField(label=u"単価")
  number = forms.IntegerField(label=u"個数")
  subtotal = forms.IntegerField(label=u"小計")
  memo = forms.TextField(label=u"メモ")
  category = forms.TextField(label=u"商品分類")
  

class IncomeForm(forms.Form):
  date = forms.DateField(label="日付")
  amount = forms.IntegerField(label="金額")
  source = forms.TextField(label="収入元")
  memo = forms.TextField(label="メモ")

class ReceiptForm(forms.Form):
  date = forms.DateField(label="日付")
  sum = forms.IntegerField(label="金額")
  place = forms.TextField(label="場所")
  memo = forms.TextField(label="メモ")

class NotebookForm(forms.Form):
  name = forms.TextField(label=u"お小遣いノートの名前", required=True)
  in_goal = forms.IntegerField(label=u"１ヶ月でもらえる金額")
  out_goal = forms.IntegerField(label=u"１ヶ月で使う金額", )
  is_main = forms.BooleanField(label=u"メインで使う")
  is_itemized = forms.BooleanField(label=u"明細も記録する")
  memo = forms.TextField(label=u"メモ")


class ProfileForm(forms.Form):
  nickname = forms.TextField(label="ニックネーム", required=True)

  def validate_nickname(self, value):
    profiles = Profile.gql("WHERE nickname=:1", value)
    if profiles.count() >= 1:
      raise ValidationError(u"このニックネームは既につかわれています")
