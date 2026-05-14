from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart


@receiver(user_logged_in)
def merge_guest_cart(sender, request, user, **kwargs):
    session_cart_id = request.session.get("cart_id")

    if not session_cart_id:
        return

    guest_cart = Cart.objects.filter(
        id=session_cart_id,
        user__isnull=True
    ).first()

    if not guest_cart:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():
        existing = user_cart.items.filter(product=item.product).first()

        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()

    guest_cart.delete()
    request.session.pop("cart_id", None)