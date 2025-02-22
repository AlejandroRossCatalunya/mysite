from django import forms
from django.contrib.auth.models import Group
from django.core import validators
from django.utils.translation import gettext_lazy as _, ngettext
from .models import Product, Order



# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=1000)
#     price = forms.DecimalField(min_value=1000, max_value=1000000, decimal_places=2)
#     description = forms.CharField(label="Product description",
#                                   widget=forms.Textarea(attrs={"rows": "10",
#                                                                "cols": "40"}),
#                                   validators=[validators.RegexValidator(
#                                       regex=r"great",
#                                       message="Must"
#                                   )])

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "color", "description", "price", "discount", "preview"
        labels = {
            "name": _("Product form name"),
            "color": _("Product form color"),
            "description": _("Product form description"),
            "price": _("Product form price"),
            "discount": _("Product form discount"),
            "preview": _("Product form preview"),
        }

    images = MultipleFileField(label=_("Select files formfield"), required=False)


class OrderForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True)
    class Meta:
        model = Order
        fields = "user", "delivery_address", "promocode", "products"


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
