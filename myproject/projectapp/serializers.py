from rest_framework import serializers
from .models import Menu, FoodCategory, UserProfile, Restaurant,Table,Order,OrderItem
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    restaurant_id = serializers.IntegerField(source='restaurant.id', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'is_staff', 'is_admin', 'restaurant_id', 'restaurant_name']

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address']

class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ['id', 'name', 'description']


class MenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category = FoodCategorySerializer(read_only=True)  
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=FoodCategory.objects.all(),
        write_only=True,
        source='category'
    )
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(),
        write_only=True,
        source='restaurant'
    )


    class Meta:
        model = Menu
        fields = ['id', 'name', 'description', 'price', 'image', 'image_url', 'category', 'category_id','restaurant_id']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else ""
    
    
    
class TableSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(),
        write_only=True,
        source='restaurant'
    )
    name = serializers.CharField(read_only=True)
    table_id = serializers.CharField(read_only=True)

    class Meta:
        model = Table
        fields = ['id', 'name', 'table_id', 'restaurant_id']
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'menu_item_name', 'quantity']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=False, read_only=False)
    table_name = serializers.CharField(source='table.name', read_only=True)
    table_id = serializers.CharField(source='table.table_id', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id', 'table', 'table_name', 'table_id', 'restaurant',
            'order_time', 'status', 'total_cost', 'items'
        ]
        read_only_fields = ['order_id', 'order_time', 'total_cost']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0
        for item in items_data:
            menu_item = item['menu_item']
            quantity = item['quantity']
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            total += menu_item.price * quantity
        order.total_cost = total
        order.save()
        return order
