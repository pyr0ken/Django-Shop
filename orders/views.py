from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .cart import Cart
from .forms import CartAddForm, CouponApplyForm, AddressForm
from category.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem, Coupon
import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from suds.client import Client


# Create your views here.

class CartView(View):
    template_name = 'orders/cart.html'

    def get(self, request):
        cart = Cart(request)
        return render(request, self.template_name, {'cart': cart})


class CartAddView(View):

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')


class CartRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderDetailView(LoginRequiredMixin, View):
    form_class = CouponApplyForm
    form_address = AddressForm
    template_name = 'orders/order.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, self.template_name,
                      {'order': order, 'form': self.form_class, 'form_address': self.form_address})

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        address = request.POST['address']
        order.address = address
        order.save()
        messages.success(request, 'your address added. now you can pey the order', 'success')
        return redirect('orders:order_detail', order_id)



class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            messages.warning(request, 'Your cart is empty !', 'warning')
            return redirect('orders:cart')
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        return redirect('orders:order_detail', order.id)


class CouponApplyView(View):
    form_class = CouponApplyForm

    def post(self, request, order_id):
        now = datetime.datetime.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code=code, valid_from__lte=now, valid_to__gte=now, active=True)
            except Coupon.DoesNotExist:
                messages.error(request, 'coupon is not exist!', 'danger')
                return redirect('orders:order_detail', order_id)
            order = Order.objects.get(id=order_id)
            order.discount = coupon.discount
            order.save()
        return redirect('orders:order_detail', order_id)


"""
    Zarinpal config
"""

if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
ZARINPAL_WEBSERVICE = f'https://{sandbox}.zarinpal.com/pg/services/WebGate/wsdl'  # Required
CallbackURL = 'http://127.0.0.1:8000/orders/verify/'  # TODO: Important: need to edit for really server.
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required


class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        if order.address:
            request.session['order_pay'] = {
                'order_id': order.id,
            }
            client = Client(ZARINPAL_WEBSERVICE)
            result = client.service.PaymentRequest(settings.MERCHANT,
                                                   order.get_total_price(),
                                                   description,
                                                   request.user.email,
                                                   request.user.phone_number,
                                                   CallbackURL)
            if result.Status == 100:
                return redirect(ZP_API_STARTPAY + result.Authority)
            else:
                return HttpResponse('Error')
        messages.error(request, 'Please add your address.', 'danger')
        return redirect('orders:order_detail', order_id)


class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.session['order_pay']['order_id']
        order = Order.objects.get(id=int(order_id))
        client = Client(ZARINPAL_WEBSERVICE)
        if request.GET.get('Status') == 'OK':
            result = client.service.PaymentVerification(settings.MERCHANT,
                                                        request.GET['Authority'],
                                                        order.get_total_price(), )
            status_code = result.Status
            if status_code == 100:
                order.pied = True
                order.RefID = result.RefID
                order.save()
                return render(request, 'orders/verify_transaction.html', {'RefID': str(result.RefID)})
            elif result.Status == 101:
                return render(request, 'orders/submitted_transaction.html', {'status_code': status_code})
            else:
                return render(request, 'orders/failed_transaction.html', {'status_code': status_code})
        else:
            return render(request, 'orders/canceled_transaction.html')
