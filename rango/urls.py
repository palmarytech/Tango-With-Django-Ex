from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    # path('about/', views.about, name='about'),
    path('category/<slug:category_name_slug>/', views.ShowCategoryView.as_view(), name='show_category'),
    path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', views.AddPageView.as_view(), name='add_page'),
    # path('login/', views.user_login, name='login'),
    path('restricted/', views.RestricteView.as_view(), name='restricted'),
    # path('logout/', views.user_logout, name='logout'),
    # path('search/', views.search, name='search'),
    path('goto/', views.GotoUrlView.as_view(), name='goto'),
    path('register-profile/', views.RegisterProfileView.as_view(), name='register_profile'),
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/', views.ListProfileView.as_view(), name='list_profile'),
    path('like_category/', views.LikeCategoryView.as_view(), name='like_category'),
    path('suggest/', views.CategorySuggestionView.as_view(), name='suggest'),
    path('search_add_pages/', views.SearchAddPageView.as_view(), name='search_add_pages'),
    path('conn_server/', views.ConnSeverView.as_view(), name='conn_server'),

]