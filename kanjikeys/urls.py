from django.urls import path

from . import views, promenad

urlpatterns = [
    path('', views.kanji, name='index'),
    #path('', views.index, name='index'),
    path('translate/', views.translate),
    path('lesson/', views.lesson),
    path('lessons/', views.lesson_list),
    path('promenad/', promenad.promenad, {'kanji_id': 0}),
    #path('promenad/(?P<kanji_id>[\w\d]+)/', promenad.promenad),
    path('promenad/<slug:kanji_id>/', promenad.promenad),
    path('stats/', views.stats),
    #path('overview/(?P<username>[\w\d_]+)/', views.stats_overview),
    path('overview/<slug:username>/', views.stats_overview),
    path('pie/', views.stats_pie),
    #path('kanjicard/(?P<kanji_id>\d+)/', views.kanjicard),
    path('kanjicard/<int:kanji_id>)/', views.kanjicard),
    #path('pdf-lesson/(?P<lesson_id>\d+)/', views.complete_lesson),
    path('pdf-lesson/<int:lesson_id>/', views.complete_lesson),
]
