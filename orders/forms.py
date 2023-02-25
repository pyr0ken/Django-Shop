from django import forms
from .models import Order


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=9)


class CouponApplyForm(forms.Form):
    code = forms.CharField(
        label='Coupon Code ',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col-md-3'
            }
        )
    )


class AddressForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'address',
        )
        labels ={
            'address': 'Address '
        }

        def __init__(self, *args, **kwargs):
            super(AddressForm, self).__init__(*args, *kwargs)
            self.fields['address'].widget.attrs['placeholder'] = 'Please enter your address:'
            self.fields['address'].widget.attrs['class'] = 'form-control col-md-3'
