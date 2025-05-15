# app/urls.py

from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet, FoodCategoryViewSet, RestaurantViewSet,TableViewSet,OrderViewSet,StaffViewSet



router = DefaultRouter()
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'categories', FoodCategoryViewSet, basename='categories')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'tables', TableViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'staff', StaffViewSet, basename='staff')
urlpatterns = [
    path('', views.index, name='index'),

    path('api/', include(router.urls)),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:restaurant_id>/menu_manage/', views.menu_manage, name='menu_manage'),
    path('restaurants/<int:restaurant_id>/cat_manage/', views.cat_manage, name='cat_manage'),
    path('restaurants/<int:restaurant_id>/table_manage/', views.table_manage, name='table_manage'),
    path('restaurants/<int:restaurant_id>/stuff_manage/', views.staff_manage, name='staff_manage'),
    path('restaurants/<int:restaurant_id>/orders_manage/', views.orders_manage, name='order_manage'),
    path('qrcode/<int:restaurant_id>/<int:table_id>/', views.table_qr, name='table_qrcode'),
    path('order/<int:restaurant_id>/<int:table_id>/', views.order_page, name='order_page'),

    # path('restaurants/<int:restaurant_id>/menu_manage/', views.menu_manage, name='menu_manage'),
]