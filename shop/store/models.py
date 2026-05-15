from django.db import models
from django.contrib.auth.models import User


# Производитель
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Категория
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Товар
class Product(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    # Скидочная цена
    discount_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="products"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    image = models.URLField(
        blank=True
    )

    rating = models.IntegerField(
        default=5
    )

    # Есть ли товар в наличии
    in_stock = models.BooleanField(
        default=True
    )

    # Итоговая цена
    def final_price(self):
        if self.discount_price:
            return self.discount_price

        return self.price

    def __str__(self):
        return self.name


# Корзина
class Cart(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Общая стоимость корзины
    def total_price(self):
        return sum(
            item.total_price()
            for item in self.items.all()
        )

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"

        return f"Cart {self.id}"


# Товар в корзине
class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    # Стоимость позиции
    def total_price(self):
        return self.product.final_price() * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# Заказ
class Order(models.Model):

    customer_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Статус заказа
    status = models.CharField(
        max_length=50,
        default="Processing"
    )

    # Общая стоимость заказа
    def total_price(self):
        return sum(
            item.total_price()
            for item in self.items.all()
        )

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

# Товар в заказе
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    # Стоимость позиции
    def total_price(self):
        return self.product.final_price() * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"