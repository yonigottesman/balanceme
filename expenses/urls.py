from django.urls import path

from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.index, name='index'),
    path('filter_index', views.filter_index, name='filter_index'),
    path('index_action', views.index_action, name='index_action'),
    path('add_txn', views.add_txn, name='add_txn'),
    path('stats', views.stats, name='stats'),

    #TODO what is name convention for post path?
    path('add_txn_post', views.add_txn_post, name='add_txn_post'),
    path('add_txn_file_post', views.add_txn_file_post, name='add_txn_file_post'),

    # ex: /expenses/5/
    path('<int:txn_id>/', views.detail, name='detail'),
    # ex: /expenses/5/edit_txn/
    path('<int:txn_id>/edit_txn/', views.edit_txn, name='edit_txn'),
    path('categories', views.categories, name='categories'),
    path('categories_add', views.categories_add, name='categories_add'),
    path('sub_categories_add', views.sub_categories_add, name='sub_categories_add'),
    path('categories_action', views.categories_action, name='categories_action'),
    path('sub_categories_action', views.sub_categories_action, name='sub_categories_action'),
    path('rules', views.rules, name='rules'),
]