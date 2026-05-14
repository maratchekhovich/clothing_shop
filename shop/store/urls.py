from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),

    # 🛍 корзина
    path('cart/', views.cart, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove'),
    path('plus/<int:item_id>/', views.increase_quantity, name='plus'),
    path('minus/<int:item_id>/', views.decrease_quantity, name='minus'),

    # 📦 заказ
    path('order/', views.create_order, name='order'),

    # 👤 профиль
    path('profile/', views.profile, name='profile'),

    # 🔐 регистрация
    path('signup/', views.signup, name='signup'),

    path("create-order/", views.create_order, name="create_order"),

]