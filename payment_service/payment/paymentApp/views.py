from rest_framework.decorators import api_view
from rest_framework.response import Response
from payment.paymentApp.models import Payment
from payment.paymentApp.paypal_service import capture_paypal_order


@api_view(["GET"])
def get_payment(request, order_id):
    """
    El frontend consulta esto para obtener el approval_url
    y redirigir al usuario a PayPal.
    """
    try:
        payment = Payment.objects.get(order_id=order_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    # Reconstruir approval_url desde el paypal_order_id guardado
    approval_url = f"https://www.sandbox.paypal.com/checkoutnow?token={payment.paypal_order_id}"

    return Response({
        "order_id": str(payment.order_id),
        "paypal_order_id": payment.paypal_order_id,
        "amount": str(payment.amount),
        "status": payment.status,
        "approval_url": approval_url,
    })


@api_view(["POST"])
def capture_payment(request, paypal_order_id):
    """
    Se llama después de que el usuario aprueba en PayPal.
    """
    try:
        payment = Payment.objects.get(paypal_order_id=paypal_order_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    response = capture_paypal_order(paypal_order_id)

    payment.status = "COMPLETED"
    payment.save()

    return Response({
        "message": "Payment captured",
        "paypal_response": response.json()  # .json() en vez de .body
    })