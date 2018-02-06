from django.contrib import admin

from .models import Transaction, SubCategory, Category, RuleType, Rule, InputSource

admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Rule)
admin.site.register(RuleType)
admin.site.register(InputSource)

