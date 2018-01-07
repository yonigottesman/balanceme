from django.urls import path

from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:txn_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:txn_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:txn_id>/vote/', views.vote, name='vote'),
]