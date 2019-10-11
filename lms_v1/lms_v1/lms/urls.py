from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/courses', views.courses, name='courses'),
    path('/course_management', views.index, name='course_management'),
    path('/statistics', views.statistics, name='statistics'),
    path('/login', auth_views.LoginView.as_view(), name='login'),
    path('/logout', auth_views.LogoutView.as_view(), name='logout'),
    path('/course/<int:course_id>/', views.view_course, name='view_course'),
    path('/course/<int:course_id>/slide/<int:slide_id>/', views.view_slide, name='view_slide'),
    path('/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('/course/<int:course_id>/save/', views.save_course, name='save_course'),
    path('/course/<int:course_id>/remove/', views.remove_course, name='remove_course'),
    path('/course/<int:course_id>/publish/', views.publish_course, name='publish_course'),
    path('/course/new/', views.new_course, name='new_course'),
    path('/course/add/', views.add_course, name='add_course'),
    path('/course/<int:course_id>/slide/new/', views.new_slide, name='new_slide'),
    path('/course/<int:course_id>/slide/add/', views.add_slide, name='add_slide'),
    path('/course/<int:course_id>/test/new/', views.new_test, name='new_test'),
    path('/course/<int:course_id>/question/new/', views.new_question, name='new_question'),
    path('/course/<int:course_id>/question/add/', views.add_question, name='add_question'),
    path('/course/<int:course_id>/question/<int:slide_id>/edit', views.edit_question, name='edit_question'),
    path('/course/<int:course_id>/question/<int:slide_id>/save', views.save_question, name='save_question'),
    path('/course/<int:course_id>/slide/<int:slide_id>/edit', views.edit_slide, name='edit_slide'),
    path('/course/<int:course_id>/slide/<int:slide_id>/save', views.save_slide, name='save_slide'),
    path('/course/<int:course_id>/slide/<int:slide_id>/remove', views.remove_slide, name='remove_slide'),
    path('/validate_answer', views.validate_answer, name='validate_answer'),
    path('/administration', views.administration, name='administration'),
    path('/settings', views.settings, name='settings'),
    path('/catalogues', views.catalogues, name='catalogues'),
    path('/catalogue/new', views.new_catalogue, name='new_catalogue'),
    path('/catalogue/add', views.add_catalogue, name='add_catalogue'),
    path('/catalogue/<int:catalogue_id>/', views.view_catalogue, name='view_catalogue'),
    path('/admin/', admin.site.urls)
]
