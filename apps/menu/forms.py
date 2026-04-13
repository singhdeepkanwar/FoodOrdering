from django import forms
from .models import MenuCategory, MenuItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ("name", "display_order", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm"}),
            "display_order": forms.NumberInput(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm"}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ("category", "name", "description", "price", "image", "is_veg", "is_available", "display_order")
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm"}),
            "description": forms.Textarea(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm", "step": "0.01"}),
            "display_order": forms.NumberInput(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm"}),
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if restaurant:
            self.fields["category"].queryset = MenuCategory.objects.filter(restaurant=restaurant)
