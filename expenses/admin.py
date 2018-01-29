from django.contrib import admin

from .models import Transaction, SubCategory, Category, RuleType, Rule

admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Rule)
admin.site.register(RuleType)

