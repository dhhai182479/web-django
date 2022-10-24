from itertools import product
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField()
    category_parent = models.ForeignKey(
        'self', 
        blank=True, 
        null=True, 
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Category'

class Brand(models.Model):
    name = models.CharField(
        max_length=50
    )
    description = models.TextField()
    country = models.CharField(
        max_length=50
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Brand'
        
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=100
    )
    price = models.IntegerField()
    stock_quantity = models.IntegerField()
    image = models.TextField()
    detail = models.TextField()
    status = models.BooleanField(
        default=True
    ) # True là còn kinh doanh, False là hết
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Product'
        
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    img_path = models.TextField()
    
    def __str__(self):
        return f"{self.product}"
    
    class Meta:
        db_table = 'ProductImage'
    
class Promotion(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    discount =  models.IntegerField()
    start_date = models.DateField(
        default=timezone.now
    )
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.product}"
    
    class Meta:
        db_table = 'Promotion'
    
class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    create_date = models.DateField(
        default=timezone.now
    )
    total_amount = models.IntegerField(
        null=True
    )
    phone = models.CharField(
        max_length=10
    )
    address = models.TextField()
    status = models.IntegerField(
        default=0
    ) # 0: Đơn hàng tạm/giỏ hàng chưa thanh toán. 1: đơn hàng đã thanh toán
    
    class Meta:
        db_table = 'Order'
        
class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        default=1
    )
    amount = models.IntegerField()
    
    class Meta:
        db_table = 'OrderDetail'