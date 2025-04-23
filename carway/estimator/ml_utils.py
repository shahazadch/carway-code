"""
Machine learning utilities for the car value estimator.
"""
import os
import json
import pickle
from decimal import Decimal

# Import ML libraries if available
try:
    import numpy as np
    import pandas as pd
    from joblib import dump, load
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    ML_LIBRARIES_AVAILABLE = True
except ImportError:
    ML_LIBRARIES_AVAILABLE = False
    
from django.conf import settings
from listings.models import CarListing

# Feature columns used for prediction
FEATURE_COLUMNS = [
    'make', 'model', 'year', 'mileage', 'fuel_type', 
    'transmission', 'engine_size', 'body_type', 'color'
]

# Target column
TARGET_COLUMN = 'price'

def prepare_dataset():
    """
    Prepare a dataset from the CarListing model for training ML models.
    
    Returns:
        tuple: (X, y, feature_names) where X is features DataFrame, 
               y is target Series, and feature_names is list of column names
    """
    if not ML_LIBRARIES_AVAILABLE:
        return None, None, None
        
    try:
        # Get all car listings
        listings = CarListing.objects.all().values(
            'make__name', 'model__name', 'year', 'mileage', 'price',
            'fuel_type', 'transmission', 'engine_size', 'body_type', 'color'
        )
        
        if not listings:
            return None, None, None
        
        # Convert to DataFrame
        df = pd.DataFrame(list(listings))
        
        # Rename columns to match feature columns
        df = df.rename(columns={
            'make__name': 'make',
            'model__name': 'model'
        })
        
        # Ensure numeric data types
        df['year'] = pd.to_numeric(df['year'])
        df['mileage'] = pd.to_numeric(df['mileage'])
        df['price'] = pd.to_numeric(df['price'])
        
        # Extract features and target
        X = df.drop(TARGET_COLUMN, axis=1)
        y = df[TARGET_COLUMN]
        
        return X, y, X.columns.tolist()
    except Exception as e:
        print(f"Error preparing dataset: {e}")
        return None, None, None

def create_model_pipeline(model_type='random_forest'):
    """
    Create a scikit-learn pipeline for the specified model type.
    
    Args:
        model_type (str): Type of model to create (random_forest, linear, gradient_boosting)
        
    Returns:
        Pipeline: A scikit-learn pipeline
    """
    if not ML_LIBRARIES_AVAILABLE:
        return None
        
    try:
        # Identify categorical and numeric features
        categorical_features = ['make', 'model', 'fuel_type', 'transmission', 'body_type', 'color']
        numeric_features = ['year', 'mileage']
        
        # Create transformers for different column types
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        # Column transformer to apply the right transformer to each column
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', categorical_transformer, categorical_features),
                ('num', numeric_transformer, numeric_features)
            ])
        
        # Select the regressor based on model_type
        if model_type == 'linear':
            regressor = LinearRegression()
        elif model_type == 'gradient_boosting':
            regressor = GradientBoostingRegressor(
                n_estimators=100, 
                learning_rate=0.1,
                max_depth=5
            )
        else:  # default to random_forest
            regressor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        
        # Create and return the pipeline
        return Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])
    except Exception as e:
        print(f"Error creating model pipeline: {e}")
        return None

def train_model(model_type='random_forest'):
    """
    Train a machine learning model on car listing data.
    
    Args:
        model_type (str): Type of model to train (random_forest, linear, gradient_boosting)
        
    Returns:
        tuple: (model, metrics, feature_importance) where model is the trained model,
               metrics is a dict of performance metrics, and feature_importance is
               a dict of feature importance scores
    """
    # Check if ML libraries are available
    if not ML_LIBRARIES_AVAILABLE:
        return None, {"error": "Machine learning libraries are not available."}, None
    
    try:
        # Prepare dataset
        X, y, feature_names = prepare_dataset()
        if X is None or len(X) < 10:  # Need minimum data points
            return None, {"error": "Not enough data to train model"}, None
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create and train the model pipeline
        pipeline = create_model_pipeline(model_type)
        pipeline.fit(X_train, y_train)
        
        # Make predictions on test set
        y_pred = pipeline.predict(X_test)
        
        # Calculate metrics
        metrics = {
            'r_squared': r2_score(y_test, y_pred),
            'mean_absolute_error': mean_absolute_error(y_test, y_pred),
            'mean_squared_error': mean_squared_error(y_test, y_pred),
            'training_data_size': len(X)
        }
        
        # Get feature importance if available
        feature_importance = {}
        if model_type in ['random_forest', 'gradient_boosting']:
            # Get the regressor from the pipeline
            regressor = pipeline.named_steps['regressor']
            
            # Get the preprocessor and its transformers
            preprocessor = pipeline.named_steps['preprocessor']
            
            # Get the feature names after preprocessing
            cat_features = preprocessor.transformers_[0][2]
            num_features = preprocessor.transformers_[1][2]
            
            # Get the one-hot encoder to extract the feature names
            onehot = preprocessor.transformers_[0][1].named_steps['onehot']
            
            # Get the categories from the one-hot encoder
            cat_categories = onehot.categories_
            
            # Create a list of all feature names after one-hot encoding
            all_feature_names = []
            for i, col in enumerate(cat_features):
                for cat in cat_categories[i]:
                    all_feature_names.append(f"{col}_{cat}")
            all_feature_names.extend(num_features)
            
            # Get feature importances and pair them with feature names
            importances = regressor.feature_importances_
            
            # Create a dictionary of feature importances
            feature_importance = dict(zip(all_feature_names, importances.tolist()))
        
        return pipeline, metrics, feature_importance
    except Exception as e:
        print(f"Error during model training: {e}")
        return None, {"error": f"Error during model training: {e}"}, None

def predict_price(model, make, model_name, year, mileage, fuel_type, transmission, 
                  engine_size, body_type, color):
    """
    Predict car price using a trained model.
    
    Args:
        model: Trained machine learning model pipeline
        make (str): Car manufacturer
        model_name (str): Car model
        year (int): Year of manufacture
        mileage (int): Car mileage
        fuel_type (str): Fuel type
        transmission (str): Transmission type
        engine_size (str): Engine size
        body_type (str): Body type
        color (str): Car color
        
    Returns:
        float: Predicted car price
    """
    # Check if ML libraries are available
    if not ML_LIBRARIES_AVAILABLE:
        return fallback_prediction(year, mileage, engine_size)
    
    try:
        # Create a DataFrame with the input data
        input_data = pd.DataFrame({
            'make': [make],
            'model': [model_name],
            'year': [year],
            'mileage': [mileage],
            'fuel_type': [fuel_type],
            'transmission': [transmission],
            'engine_size': [engine_size],
            'body_type': [body_type],
            'color': [color]
        })
        
        # Make prediction
        prediction = model.predict(input_data)
        return float(prediction[0])
    except Exception as e:
        print(f"Error during prediction: {e}")
        # Fall back to the simple heuristic model
        return fallback_prediction(year, mileage, engine_size)

def fallback_prediction(year, mileage, engine_size):
    """
    Simple fallback prediction when ML model is not available.
    This uses basic heuristics to estimate a car's value.
    
    Args:
        year (int): Year of manufacture
        mileage (int): Car mileage
        engine_size (str): Engine size (e.g., "2.0L")
        
    Returns:
        float: Estimated car price
    """
    current_year = 2025  # Hardcoded current year
    
    # Extract numeric engine size
    try:
        engine_numeric = float(engine_size.replace('L', '').strip())
    except:
        engine_numeric = 2.0  # Default if parsing fails
    
    # Base price: newer cars are more expensive
    base_price = 30000 - (current_year - year) * 2000
    
    # Adjust for mileage: higher mileage reduces price
    mileage_factor = max(0.7, 1 - (mileage / 100000) * 0.3)
    
    # Adjust for engine size: larger engines are more expensive
    engine_factor = min(1.5, max(0.8, engine_numeric / 2.0))
    
    # Calculate estimated price
    estimated_price = base_price * mileage_factor * engine_factor
    
    # Ensure minimum price
    estimated_price = max(2000, estimated_price)
    
    return round(estimated_price, 2)