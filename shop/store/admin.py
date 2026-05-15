from django.contrib import admin
from .models import *


# =========================
# 🛍 PRODUCT ADMIN
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "discount_price",
        "in_stock",
        "rating"
    )

    list_filter = (
        "brand",
        "category",
        "in_stock"
    )

    search_fields = (
        "name",
        "description"
    )

    list_editable = (
        "price",
        "discount_price",
        "in_stock",
        "rating"
    )


# =========================
# 🏷 BRAND
# =========================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ("name",)


# =========================
# 📦 CATEGORY
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


# =========================
# 🛒 CART ITEM INLINE
# =========================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    inlines = [CartItemInline]


# =========================
# 🧺 CART ITEM
# =========================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "cart")


# =========================
# 📦 ORDER ITEM INLINE
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "status",
        "created_at"
    )

    list_filter = ("status",)

    search_fields = ("customer_name",)

    inlines = [OrderItemInline]


# =========================
# 📦 ORDER ITEM
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")