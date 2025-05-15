from django.contrib.auth.models import User
from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurants")
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)  
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True, blank=True)
    bio = models.TextField(blank=False, default="Novice Django Developer but building unique portfolio")

    def __str__(self):
        if self.is_admin:
            role = "Admin"
        elif self.is_staff:
            role = "Staff"
        else:
            role = "Other"
        return f"{self.user.username} ({role})"


class FoodCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='projectapp/menu_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
        


class Table(models.Model):
    name = models.CharField(max_length=50)
    table_id = models.CharField(max_length=20)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')

    class Meta:
        unique_together = ('restaurant', 'table_id')


class Order(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=30, primary_key=True)  
    order_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Completed", "Completed")], default="Pending")
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.order_id} (Table {self.table.id})"

    def save(self, *args, **kwargs):
        if not self.order_id:
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.order_id = f"T{self.table.id}-{timestamp}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    def get_total_price(self):
        return self.menu_item.price * self.quantity