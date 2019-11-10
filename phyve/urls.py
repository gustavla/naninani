from django.urls import path

from . import ajax

urlpatterns = [
    path('ajax.js', ajax.script_view, name='ajax'),
    path('q/<slug:function>/', ajax.response_view, name='ajax_query'),
]
