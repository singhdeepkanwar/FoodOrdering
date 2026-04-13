from django import forms
from .models import Table


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ("name", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border rounded-lg px-3 py-2 text-sm", "placeholder": "e.g. Table 1"}),
        }
