from django.contrib import admin

from .models import Transaction, SubCategory, Category

admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(SubCategory)

