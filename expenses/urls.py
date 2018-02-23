from django.urls import path

from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.index, name='index'),
    path('filter_index', views.filter_index, name='filter_index'),
    path('index_action', views.index_action, name='index_action'),
    path('add', views.add, name='add'),
    path('stats', views.stats, name='stats'),
    path('save_post/', views.save_post, name='save_post'),

    path('stats/<int:category>', views.stats_category, name='stats_category'),
    path('stats/<str:month>', views.stats_month, name='stats_month'),

    path('stats_manual', views.stats_manual, name='stats_manual'),

    #TODO what is name convention for post path?
    path('add_txn_post', views.add_txn_post, name='add_txn_post'),
    path('add_txn_file_post', views.add_txn_file_post, name='add_txn_file_post'),

    path('categories', views.categories, name='categories'),
    path('categories_add', views.categories_add, name='categories_add'),
    path('sub_categories_add', views.sub_categories_add, name='sub_categories_add'),
    path('categories_action', views.categories_action, name='categories_action'),
    path('sub_categories_action', views.sub_categories_action, name='sub_categories_action'),
    path('rules', views.rules, name='rules'),
    path('rules_add', views.rules_add, name='rules_add'),
    path('rules_action', views.rules_action, name='rules_action'),
]