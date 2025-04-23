from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime
from .models import CarListing, CarModel, CarMake
from .forms import CarListingForm, CarImageFormSet, SearchForm


class ListingListView(ListView):
    model = CarListing
    template_name = 'theme_templates/listings-grid-cars.html'
    context_object_name = 'listings'
    paginate_by = 9
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car_makes'] = CarMake.objects.all().order_by('name')
        context['year_range'] = range(datetime.now().year, 1970, -1)
        context['body_types'] = CarListing.BODY_CHOICES
        context['fuel_types'] = CarListing.FUEL_CHOICES
        context['transmission_types'] = CarListing.TRANSMISSION_CHOICES
        return context
    

class UserListingListView(ListView):
    model = CarListing
    template_name = 'listings/user_listings.html'
    context_object_name = 'listings'
    paginate_by = 5
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return CarListing.objects.filter(user=user).order_by('-created_at')


class ListingDetailView(DetailView):
    model = CarListing
    template_name = 'theme_templates/single-car.html'
    context_object_name = 'listing'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get similar listings (same make or model, different listing)
        similar_listings = CarListing.objects.filter(
            Q(make=self.object.make) | Q(model=self.object.model)
        ).exclude(id=self.object.id).order_by('-created_at')[:6]
        context['similar_listings'] = similar_listings
        return context


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = CarListing
    form_class = CarListingForm
    template_name = 'theme_templates/add-car.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CarImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = CarImageFormSet()
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save()
        
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Your listing has been created!')
            return redirect(self.get_success_url())
        return super().form_valid(form)


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CarListing
    form_class = CarListingForm
    template_name = 'listings/listing_update.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CarImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['formset'] = CarImageFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Your listing has been updated!')
            return redirect(self.get_success_url())
        
        return super().form_valid(form)
    
    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.user


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CarListing
    template_name = 'listings/listing_confirm_delete.html'
    success_url = reverse_lazy('listing-list')
    
    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your listing has been deleted!')
        return super().delete(request, *args, **kwargs)


def load_models(request):
    make_id = request.GET.get('make')
    models = CarModel.objects.filter(make_id=make_id).order_by('name')
    return render(request, 'listings/model_dropdown_list_options.html', {'models': models})


def search_listings(request):
    form = SearchForm(request.GET or None)
    query = CarListing.objects.all()
    
    if form.is_valid() and any(form.cleaned_data.values()):
        data = form.cleaned_data
        
        # Filter by make
        if data['make']:
            query = query.filter(make=data['make'])
        
        # Filter by model if make is selected
        if data['model'] and data['make']:
            query = query.filter(model=data['model'])
        
        # Filter by price range
        if data['min_price']:
            query = query.filter(price__gte=data['min_price'])
        if data['max_price']:
            query = query.filter(price__lte=data['max_price'])
        
        # Filter by year range
        if data['min_year'] and data['min_year'] != '':
            query = query.filter(year__gte=int(data['min_year']))
        if data['max_year'] and data['max_year'] != '':
            query = query.filter(year__lte=int(data['max_year']))
        
        # Filter by other attributes
        if data['fuel_type']:
            query = query.filter(fuel_type=data['fuel_type'])
        if data['transmission']:
            query = query.filter(transmission=data['transmission'])
        if data['body_type']:
            query = query.filter(body_type=data['body_type'])
    
    context = {
        'form': form,
        'listings': query,
        'search_performed': request.GET and any(request.GET.values())
    }
    return render(request, 'listings/search.html', context)
