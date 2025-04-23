from django import forms
from listings.models import CarListing, CarMake, CarModel

class EstimatorForm(forms.Form):
    """
    Form for the car value estimator
    """
    make = forms.ModelChoiceField(
        queryset=CarMake.objects.all().order_by('name'),
        required=True,
        empty_label="Select Make",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    model = forms.ModelChoiceField(
        queryset=CarModel.objects.none(),
        required=True,
        empty_label="Select Model",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    year = forms.IntegerField(
        required=True,
        min_value=1900,
        max_value=2030,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'})
    )
    
    mileage = forms.IntegerField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mileage'})
    )
    
    fuel_type = forms.ChoiceField(
        choices=CarListing.FUEL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    transmission = forms.ChoiceField(
        choices=CarListing.TRANSMISSION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    engine_size = forms.CharField(
        required=True,
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2.0L'})
    )
    
    body_type = forms.ChoiceField(
        choices=CarListing.BODY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    color = forms.ChoiceField(
        choices=CarListing.COLOR_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If there is a make selected, filter the model queryset
        if 'make' in self.data:
            try:
                make_id = int(self.data.get('make'))
                self.fields['model'].queryset = CarModel.objects.filter(make_id=make_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input, fallback to empty queryset
        elif self.initial.get('make'):
            try:
                make_id = int(self.initial.get('make'))
                self.fields['model'].queryset = CarModel.objects.filter(make_id=make_id).order_by('name')
            except (ValueError, TypeError):
                pass