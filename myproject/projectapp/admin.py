from django.contrib import admin
from .models import Restaurant, UserProfile, FoodCategory, Menu, Table, Order, OrderItem

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'owner')
    search_fields = ('name', 'address', 'owner__username')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_admin', 'is_staff', 'restaurant')
    search_fields = ('user__username', 'restaurant__name')
    list_filter = ('is_admin', 'is_staff')

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant')
    search_fields = ('name', 'restaurant__name')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant', 'category', 'price', 'available')
    search_fields = ('name', 'restaurant__name', 'category__name')
    list_filter = ('restaurant', 'category', 'available')

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'table_id', 'restaurant')
    search_fields = ('name', 'table_id', 'restaurant__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'restaurant', 'table', 'order_time', 'status', 'total_cost')
    search_fields = ('order_id', 'restaurant__name', 'table__name')
    list_filter = ('status', 'restaurant')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'menu_item', 'quantity')
    search_fields = ('order__order_id', 'menu_item__name')
