from django.urls import path

from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.index, name='index'),
    path('add_txn', views.add_txn, name='add_txn'),
    path('stats', views.stats, name='stats'),

    #TODO what is name convention for post path?
    path('add_txn_post', views.add_txn_post, name='add_txn_post'),
    path('add_txn_file_post', views.add_txn_file_post, name='add_txn_file_post'),

    # ex: /expenses/5/
    path('<int:txn_id>/', views.detail, name='detail'),
    # ex: /expenses/5/edit_txn/
    path('<int:txn_id>/edit_txn/', views.edit_txn, name='edit_txn'),
]