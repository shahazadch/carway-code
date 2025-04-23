from django import forms
from .models import CarListing, CarImage, CarModel


class CarListingForm(forms.ModelForm):
    class Meta:
        model = CarListing
        fields = ['make', 'model', 'year', 'mileage', 'price', 'fuel_type', 
                 'transmission', 'engine_size', 'body_type', 'color', 'description']
        widgets = {
            'make': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'data-searchable': 'true',
            }),
            'model': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'data-searchable': 'true',
            }),
            'year': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter mileage',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter price',
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'transmission': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'engine_size': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g., 2.0L',
            }),
            'body_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'color': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'rows': 5,
                'placeholder': 'Describe your vehicle, including its condition, features, and history',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(CarListingForm, self).__init__(*args, **kwargs)
        self.fields['model'].queryset = CarModel.objects.none()
        
        # Add year choices similar to the Finder theme
        current_year = 2025  # Set to current year
        year_choices = [(y, str(y)) for y in range(current_year, 1950, -1)]
        self.fields['year'].widget.choices = year_choices
        
        if 'make' in self.data:
            try:
                make_id = int(self.data.get('make'))
                self.fields['model'].queryset = CarModel.objects.filter(make_id=make_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.make:
            self.fields['model'].queryset = CarModel.objects.filter(make=self.instance.make)


class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }


CarImageFormSet = forms.inlineformset_factory(
    CarListing, CarImage, form=CarImageForm, extra=1, max_num=10, can_delete=True
)


class SearchForm(forms.Form):
    PRICE_CHOICES = [
        ('', 'Any'),
        ('0-5000', '0 - 5,000'),
        ('5000-10000', '5,000 - 10,000'),
        ('10000-20000', '10,000 - 20,000'),
        ('20000-30000', '20,000 - 30,000'),
        ('30000-50000', '30,000 - 50,000'),
        ('50000-100000', '50,000 - 100,000'),
        ('100000-999999999', '100,000+')
    ]
    
    YEAR_CHOICES = [('', 'Any')] + [(str(r), str(r)) for r in range(2023, 1970, -1)]
    
    make = forms.ModelChoiceField(queryset=None, required=False, empty_label="Any Make")
    model = forms.ModelChoiceField(queryset=None, required=False, empty_label="Any Model")
    min_price = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min'}))
    max_price = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max'}))
    min_year = forms.ChoiceField(choices=YEAR_CHOICES, required=False)
    max_year = forms.ChoiceField(choices=YEAR_CHOICES, required=False)
    fuel_type = forms.ChoiceField(choices=[('', 'Any')] + CarListing.FUEL_CHOICES, required=False)
    transmission = forms.ChoiceField(choices=[('', 'Any')] + CarListing.TRANSMISSION_CHOICES, required=False)
    body_type = forms.ChoiceField(choices=[('', 'Any')] + CarListing.BODY_CHOICES, required=False)
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        from .models import CarMake
        self.fields['make'].queryset = CarMake.objects.all()
        self.fields['model'].queryset = CarModel.objects.none()
        
        if 'make' in self.data:
            try:
                make_id = int(self.data.get('make'))
                self.fields['model'].queryset = CarModel.objects.filter(make_id=make_id)
            except (ValueError, TypeError):
                pass
        
        # Add placeholders
        for field_name, field in self.fields.items():
            if field_name not in ['make', 'model', 'min_year', 'max_year', 'fuel_type', 'transmission', 'body_type']:
                placeholder = ' '.join(word.capitalize() for word in field_name.split('_'))
                field.widget.attrs['placeholder'] = placeholder
