from django import forms
from core.models import Trip, Location


class ReturnVehicleForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['end_location']

    end_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), required=True, label='End Location'
    )
