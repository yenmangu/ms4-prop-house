from django import forms
from django.utils import timezone


class PropHireForm(forms.Form):
    """
    PropHireForm Hire selection form for capturing logistics data

    Args:
        forms: _description_
    """

    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "industrial-input",
                "min": timezone.now().date().isoformat(),
            }
        ),
        label="Hire Start Date",
    )

    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "industrial-input",
                "min": timezone.now().date().isoformat(),
            }
        ),
        label="Hire End Date",
    )

    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "industrial-input",
            },
        ),
    )

    production_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "industrial-input",
                "placeholder": "e.g. Project X",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end <= start:
            raise forms.ValidationError("The return date must be after the start date.")
        return cleaned_data
