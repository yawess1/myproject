from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from .models import UserProfile, Restaurant, Menu, FoodCategory,Table,Order,OrderItem
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import FormView
from django.db.models import Q, Max, F, Func, IntegerField
from django.db.models.functions import Cast
from .forms import RestaurantAdminRegistrationForm
from django.shortcuts import redirect

from pydantic import BaseModel, Field, ValidationError
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from rest_framework.permissions import IsAuthenticated 


from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import MenuSerializer, FoodCategorySerializer, RestaurantSerializer,TableSerializer,OrderItemSerializer,OrderCreateSerializer, UserProfileSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import permissions
from .forms import UserRegistrationForm
import qrcode




def index(request):
    return render(request, "landingpage.html")



class IsRestaurantOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.restaurant.owner == request.user
  
class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        qs = self.queryset
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)

        category_id = self.request.query_params.get('category_id')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        restaurant_id = self.request.data.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=self.request.user)
        serializer.save(restaurant=restaurant)



class FoodCategoryViewSet(viewsets.ModelViewSet):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        qs = self.queryset.filter(restaurant__owner=self.request.user)
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs

    def perform_create(self, serializer):
        restaurant_id = self.request.data.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=self.request.user)
        serializer.save(restaurant=restaurant)



class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        qs = self.queryset.filter(restaurant__owner=self.request.user)
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs

    def perform_create(self, serializer):
        print("perform_create called")  
        restaurant = get_object_or_404(Restaurant, id=self.request.data.get('restaurant_id'))
        max_table_num = (
            Table.objects.filter(restaurant=restaurant)
            .annotate(num_part=Cast(F('table_id')[1:], IntegerField()))
            .aggregate(max_num=Max('num_part'))['max_num'] or 0
        )
        next_number = max_table_num + 1
        table_id = f"T{next_number:03d}"
        name = f"Table {next_number}"
        serializer.save(restaurant=restaurant, table_id=table_id, name=name)

    def create(self, request, *args, **kwargs):
        print("create called")  
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)
        
        
        
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_time')
    serializer_class = OrderCreateSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []  
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        restaurant_id = self.request.query_params.get('restaurant_id')
        status = self.request.query_params.get('status')
        qs = self.queryset
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        if status:
            qs = qs.filter(status=status)
        if user.is_authenticated:
            if hasattr(user, 'userprofile'):
                profile = user.userprofile
                if profile.is_admin:
                    qs = qs.filter(restaurant__owner=user)
                elif profile.is_staff:
                    qs = qs.filter(restaurant=profile.restaurant)
                else:
                    qs = qs.none()
            else:
                qs = qs.none()
        print("user:", user, "profile.restaurant:", getattr(user.userprofile, 'restaurant', None), "restaurant_id:", restaurant_id)
        return qs
    
@login_required
def menu_manage(request, restaurant_id):
    profile = request.user.userprofile
    if profile.is_staff:
        return HttpResponseForbidden("You are not allowed to access this restaurant's menu management")
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    menu_items = Menu.objects.filter(restaurant=restaurant)
    food_categories = FoodCategory.objects.filter(restaurant=restaurant)
    return render(request, "manage_account/menu_manage.html", {
        "restaurant": restaurant,
        "restaurant_id": restaurant_id,
        "menu_items": menu_items,
        "food_categories": food_categories,
    })

@login_required
def cat_manage(request, restaurant_id):
    profile = request.user.userprofile
    if profile.is_staff:
        return HttpResponseForbidden("You are not allowed to access this restaurant's category management")
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    categories = restaurant.categories.all()
    return render(request, "manage_account/cat_manage.html", {
        "restaurant_name": restaurant.name,
        "restaurant": restaurant,
        "restaurant_id": restaurant_id,
        "categories": categories,
    })

@login_required
def table_manage(request, restaurant_id):
    profile = request.user.userprofile
    if profile.is_staff:
        return HttpResponseForbidden("员工无权访问餐桌管理")
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    tables = restaurant.tables.all()
    return render(request, "manage_account/table_manage.html", {
        "restaurant_name": restaurant.name,
        "restaurant": restaurant,
        "restaurant_id": restaurant_id,
        "tables": tables,
    })
    
@login_required
def restaurant_list(request):
    profile = request.user.userprofile
    if profile.is_staff:

        restaurants = Restaurant.objects.filter(id=profile.restaurant.id)
    else:

        restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, "manage_account/restaurant_list.html", {
        "restaurants": restaurants
    })


def table_qr(request, restaurant_id, table_id):
    order_url = request.build_absolute_uri(
        f'/myproject/order/{restaurant_id}/{table_id}/'
    )
    img = qrcode.make(order_url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

def order_page(request, restaurant_id, table_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    table = get_object_or_404(Table, id=table_id, restaurant=restaurant)
    categories = FoodCategory.objects.filter(restaurant=restaurant)
    menu_items = Menu.objects.filter(restaurant=restaurant)
    return render(request, 'order.html', {
        'restaurant': restaurant,
        'table': table,
        'categories': categories,
        'menu_items': menu_items,
    })
        
        

class StaffViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.filter(is_staff=True, is_admin=False)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        restaurant_id = self.request.query_params.get('restaurant_id')
        qs = UserProfile.objects.filter(is_staff=True, is_admin=False)
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        else:

            qs = qs.filter(restaurant__owner=user)
        return qs

    def create(self, request, *args, **kwargs):
        user = request.user
        restaurant_id = request.data.get('restaurant_id')
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not (restaurant_id and username and email and password):
            return Response({'detail': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=user)
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        new_user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile.objects.create(user=new_user, is_admin=False, is_staff=True, restaurant=restaurant)
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        if instance.restaurant.owner != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        user = instance.user
        self.perform_destroy(instance)
        user.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
def staff_manage(request, restaurant_id):
    profile = request.user.userprofile
    if profile.is_staff:
        return HttpResponseForbidden("You are not allowed to access this restaurant's staff management")
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    staff_list = UserProfile.objects.filter(restaurant=restaurant, is_staff=True, is_admin=False)
    return render(request, "manage_account/staff_manage.html", {
        "restaurant": restaurant,
        "staff_list": staff_list,
    })


@login_required
def orders_manage(request, restaurant_id):
    profile = request.user.userprofile
    if profile.is_staff:
        # 只允许访问自己被分配的餐厅
        if profile.restaurant.id != int(restaurant_id):
            return HttpResponseForbidden("You are not allowed to access this restaurant's orders")
        restaurant = profile.restaurant
    else:
        # 运营者只能管理自己餐厅
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    return render(request, "manage_account/orders_manage.html", {
        "restaurant_id": restaurant.id,
        "restaurant": restaurant,
    })
    
