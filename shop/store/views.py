from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Category,
    Brand
)

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


# =========================
# 🧾 РЕГИСТРАЦИЯ
# =========================
class SignUpForm(UserCreationForm):
    username = forms.CharField(label="Имя пользователя")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


# =========================
# 🛒 КОРЗИНА
# =========================
def get_cart(request):

    # Авторизованный пользователь
    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        return cart

    # Гость
    cart_id = request.session.get("cart_id")
    cart = None

    if cart_id:
        cart = Cart.objects.filter(id=cart_id).first()

    if not cart:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id

    return cart


def get_cart_count(request):

    cart = get_cart(request)

    return sum(item.quantity for item in cart.items.all())


# =========================
# 🏠 ГЛАВНАЯ
# =========================
def home(request):

    products = Product.objects.all()[:6]

    new_products = Product.objects.all().order_by('-id')[:6]

    sale_products = Product.objects.filter(
        discount_price__isnull=False
    )[:6]

    return render(request, "home.html", {
        "products": products,
        "new_products": new_products,
        "sale_products": sale_products,
        "cart_count": get_cart_count(request)
    })


# =========================
# 🛍 ВСЕ ТОВАРЫ
# =========================
def products(request):

    products = Product.objects.all()

    # 🔍 Поиск
    query = request.GET.get("q")

    if query:
        products = products.filter(
            name__icontains=query
        )

    # 📂 Категория
    category_id = request.GET.get("category")

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    # 🏷 Бренд
    brand_id = request.GET.get("brand")

    if brand_id:
        products = products.filter(
            brand_id=brand_id
        )

    # 💰 Сортировка
    sort = request.GET.get("sort")

    if sort == "cheap":
        products = products.order_by("price")

    elif sort == "expensive":
        products = products.order_by("-price")

    elif sort == "new":
        products = products.order_by("-id")

    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request, "products.html", {
        "products": products,
        "categories": categories,
        "brands": brands,
        "cart_count": get_cart_count(request)
    })


# =========================
# ➕ ДОБАВИТЬ В КОРЗИНУ
# =========================
def add_to_cart(request, product_id):

    cart = get_cart(request)

    product = get_object_or_404(
        Product,
        id=product_id
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    messages.success(
        request,
        f"✅ {product.name} добавлен в корзину"
    )

    return redirect(request.META.get("HTTP_REFERER", "/products/"))


# =========================
# ❌ УДАЛИТЬ
# =========================
def remove_from_cart(request, item_id):

    cart = get_cart(request)

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    item.delete()

    return redirect("cart")


# =========================
# ➕ УВЕЛИЧИТЬ
# =========================
def increase_quantity(request, item_id):

    cart = get_cart(request)

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    item.quantity += 1
    item.save()

    return redirect("cart")


# =========================
# ➖ УМЕНЬШИТЬ
# =========================
def decrease_quantity(request, item_id):

    cart = get_cart(request)

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


# =========================
# 🛒 КОРЗИНА
# =========================
def cart(request):

    cart = get_cart(request)

    items = cart.items.all()

    total = sum(
        item.total_price()
        for item in items
    )

    return render(request, "cart.html", {
        "items": items,
        "total": total,
        "cart_count": get_cart_count(request)
    })


# =========================
# 📦 ЗАКАЗ
# =========================
def create_order(request):

    cart = get_cart(request)

    items = cart.items.all()

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")

        if not name or not email:
            return redirect("cart")

        order = Order.objects.create(
            customer_name=name,
            email=email
        )

        total = 0

        for item in items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

            total += item.total_price()

        # HTML письмо
        html_content = render_to_string(
            "emails/order_receipt.html",
            {
                "order": order,
                "items": items,
                "total": total,
            }
        )

        # Текстовая версия
        text_content = strip_tags(html_content)

        # Отправка email
        email_message = EmailMultiAlternatives(
            subject="🧾 Ваш чек | SHOP",
            body=text_content,
            from_email=None,
            to=[email]
        )

        email_message.attach_alternative(
            html_content,
            "text/html"
        )

        email_message.send()

        # очистка корзины
        items.delete()

        messages.success(
            request,
            "🎉 Оплата прошла успешно! Чек отправлен на вашу почту."
        )

        return redirect("cart")

    total = sum(
        item.total_price()
        for item in items
    )

    return render(request, "order.html", {
        "items": items,
        "total": total,
        "cart_count": get_cart_count(request)
    })
# =========================
# 👤 PROFILE
# =========================
def profile(request):

    return render(request, "profile.html", {
        "cart_count": get_cart_count(request)
    })


# =========================
# 🔐 SIGNUP
# =========================
def signup(request):

    if request.method == 'POST':

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('/')

    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {
        'form': form
    })
