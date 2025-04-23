from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from decimal import Decimal

from .models import PriceModel, PricePrediction
from .forms import EstimatorForm
from .ml_utils import train_model, predict_price, fallback_prediction

def estimator_home(request):
    """
    View for the car value estimator homepage.
    This is the main page where users can enter car details to get price estimates.
    """
    prediction = None
    error_message = None
    recent_predictions = []
    
    # Get recent predictions for the sidebar
    if request.user.is_authenticated:
        recent_predictions = PricePrediction.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        # Get anonymous predictions from session if available
        session_predictions = request.session.get('recent_predictions', [])
        for pred_id in session_predictions:
            try:
                pred = PricePrediction.objects.get(id=pred_id)
                recent_predictions.append(pred)
            except PricePrediction.DoesNotExist:
                pass
    
    # Process form submission
    if request.method == 'POST':
        form = EstimatorForm(request.POST)
        if form.is_valid():
            # Extract form data
            make = form.cleaned_data['make'].name
            model_name = form.cleaned_data['model'].name
            year = form.cleaned_data['year']
            mileage = form.cleaned_data['mileage']
            fuel_type = form.cleaned_data['fuel_type']
            transmission = form.cleaned_data['transmission']
            engine_size = form.cleaned_data['engine_size']
            body_type = form.cleaned_data['body_type']
            color = form.cleaned_data['color']
            
            # Get active ML model
            active_model = PriceModel.get_active_model()
            
            if active_model:
                # Load the ML model object
                ml_model = active_model.get_model_object()
                
                if ml_model:
                    # Make prediction using ML model
                    predicted_price = predict_price(
                        ml_model, make, model_name, year, mileage, 
                        fuel_type, transmission, engine_size, body_type, color
                    )
                else:
                    # Use fallback prediction if model couldn't be loaded
                    predicted_price = fallback_prediction(year, mileage, engine_size)
            else:
                # Use fallback prediction if no model exists
                predicted_price = fallback_prediction(year, mileage, engine_size)
            
            if predicted_price:
                # Create prediction record
                prediction = PricePrediction.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    model=active_model,
                    make=make,
                    model_name=model_name,
                    year=year,
                    mileage=mileage,
                    fuel_type=fuel_type,
                    transmission=transmission,
                    engine_size=engine_size,
                    body_type=body_type,
                    color=color,
                    predicted_price=Decimal(str(predicted_price)),
                    input_data={
                        'make': make,
                        'model': model_name,
                        'year': year,
                        'mileage': mileage,
                        'fuel_type': fuel_type,
                        'transmission': transmission,
                        'engine_size': engine_size,
                        'body_type': body_type,
                        'color': color
                    }
                )
                
                # Store prediction ID in session for anonymous users
                if not request.user.is_authenticated:
                    recent_pred_ids = request.session.get('recent_predictions', [])
                    if prediction.id not in recent_pred_ids:
                        recent_pred_ids.insert(0, prediction.id)
                        # Keep only the 5 most recent
                        recent_pred_ids = recent_pred_ids[:5]
                        request.session['recent_predictions'] = recent_pred_ids
                
                # Immediately add to recent predictions for the view
                if prediction not in recent_predictions:
                    recent_predictions = [prediction] + list(recent_predictions)[:4]
            else:
                error_message = "Unable to generate a price estimate for the provided car details."
    else:
        form = EstimatorForm()
    
    context = {
        'form': form,
        'prediction': prediction,
        'error_message': error_message,
        'recent_predictions': recent_predictions
    }
    
    return render(request, 'theme_templates/estimator/estimator_home.html', context)

@login_required
def manage_models(request):
    """
    View for managing ML models.
    Admin users can view, create, and delete models.
    """
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('estimator-home')
    
    # Get all models ordered by creation date
    model_list = PriceModel.objects.all()
    
    # Paginate results
    paginator = Paginator(model_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'theme_templates/estimator/manage_models.html', {'page_obj': page_obj})

@login_required
def train_new_model(request):
    """
    View for training a new ML model.
    Admin users can specify model parameters and train a new model.
    """
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('estimator-home')
    
    if request.method == 'POST':
        name = request.POST.get('model_name')
        description = request.POST.get('model_description', '')
        model_type = request.POST.get('model_type', 'random_forest')
        
        if not name:
            messages.error(request, "Please provide a name for the model.")
            return render(request, 'theme_templates/estimator/train_model.html')
        
        # Train new model
        model_pipeline, metrics, feature_importance = train_model(model_type)
        
        if model_pipeline and 'error' not in metrics:
            # Create new model record
            new_model = PriceModel(
                name=name,
                description=description,
                model_type=model_type,
                r_squared=metrics.get('r_squared'),
                mean_absolute_error=metrics.get('mean_absolute_error'),
                mean_squared_error=metrics.get('mean_squared_error'),
                training_data_size=metrics.get('training_data_size'),
                feature_importance=feature_importance,
                is_active=True  # Make this the active model
            )
            
            # Save the model object
            new_model.save()
            new_model.set_model_object(model_pipeline)
            
            messages.success(request, f"Model '{name}' has been successfully trained and is now active.")
            return redirect('manage-models')
        else:
            error = metrics.get('error', "Failed to train model. Please try again later.")
            messages.error(request, error)
    
    return render(request, 'theme_templates/estimator/train_model.html')

@login_required
def set_active_model(request, model_id):
    """
    Set a specific model as the active one for predictions.
    """
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('estimator-home')
    
    model = get_object_or_404(PriceModel, id=model_id)
    model.is_active = True
    model.save()  # This will deactivate all other models due to the save() method override
    
    messages.success(request, f"Model '{model.name}' is now active for predictions.")
    return redirect('manage-models')

@login_required
def delete_model(request, model_id):
    """
    Delete a specific model.
    """
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('estimator-home')
    
    model = get_object_or_404(PriceModel, id=model_id)
    model_name = model.name
    
    # If this is the active model, we need to set another one as active
    is_active = model.is_active
    model.delete()
    
    if is_active:
        # Set the most recent model as active, if any exist
        latest_model = PriceModel.objects.first()
        if latest_model:
            latest_model.is_active = True
            latest_model.save()
    
    messages.success(request, f"Model '{model_name}' has been deleted.")
    return redirect('manage-models')