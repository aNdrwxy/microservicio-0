from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .rabbitmq import publish_event

from orden.ordenApp.services import get_game_details
from orden.ordenApp.models import Cart, CartItem, Order
from orden.ordenApp.serializers import CartSerializer, CartItemSerializer, OrderSerializer
from orden.ordenApp.permissions import IsAuthenticatedUser


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedUser]

    def _get_or_create_cart(self, user_id):
        cart, created = Cart.objects.get_or_create(
            user_id=user_id,
            status='ACTIVE'
        )
        return cart

    def list(self, request):
        user_id = request.user.token.payload.get("user_id")
        cart = self._get_or_create_cart(user_id)

        items = cart.items.all()
        enriched_items = []

        for item in items:
            game_data = get_game_details(str(item.game_id))

            if game_data:
                enriched_items.append({
                    "id": str(item.id),
                    "game_id": str(item.game_id),
                    "title": game_data.get("title"),
                    "price": game_data.get("price"),
                    "cover_image": game_data.get("cover_image"),
                    "added_at": item.added_at
                })
            else:
                enriched_items.append({
                    "id": str(item.id),
                    "game_id": str(item.game_id),
                    "title": "Unknown Game",
                    "price": "0.00",
                    "cover_image": None,
                    "added_at": item.added_at
                })

        return Response({
            "id": str(cart.id),
            "user_id": str(cart.user_id),
            "status": cart.status,
            "items": enriched_items,
            "created_at": cart.created_at
        })

    @action(detail=False, methods=['post'])
    def add_item(self, request):

        user_id = request.user.token.payload.get("user_id")
        game_id = request.data.get("game_id")

        if not game_id:
            return Response({"error": "game_id es requerido"}, status=400)

        game_data = get_game_details(game_id)

        if not game_data:
            return Response({"error": "El juego no existe o no está disponible"}, status=404)

        cart = self._get_or_create_cart(user_id)

        if CartItem.objects.filter(cart=cart, game_id=game_id).exists():
            return Response({"message": "El juego ya está en el carrito"}, status=200)

        CartItem.objects.create(cart=cart, game_id=game_id)

        return Response({"message": "Juego agregado al carrito"}, status=201)


    @action(detail=False, methods=['delete'])
    def remove_item(self, request):

        user_id = request.user.token.payload.get("user_id")
        game_id = request.data.get("game_id")

        cart = self._get_or_create_cart(user_id)

        item = get_object_or_404(CartItem, cart=cart, game_id=game_id)
        item.delete()

        return Response({"message": "Juego eliminado del carrito"}, status=204)
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):

        user_id = request.user.token.payload.get("user_id")
        cart = self._get_or_create_cart(user_id)

        if cart.status != 'ACTIVE':
            return Response({"error": "Este carrito ya fue procesado"}, status=400)

        items = cart.items.all()

        if not items.exists():
            return Response({"error": "El carrito está vacío"}, status=400)

        total = Decimal('0.00')

        for item in items:
            game_data = get_game_details(str(item.game_id))

            if not game_data:
                return Response(
                    {"error": f"El juego {item.game_id} ya no está disponible"},
                    status=400
                )

            price = Decimal(game_data['price'])
            total += price

        order = Order.objects.create(
            user_id=user_id,
            cart=cart,
            total_amount=total,
            status='PENDING'
        )

        event_data = {
            "order_id": str(order.id),
            "user_id": str(user_id),
            "total_amount": str(total)
        }

        publish_event("order_created", event_data)

        cart.status = 'CHECKED_OUT'
        cart.save()

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=201)

