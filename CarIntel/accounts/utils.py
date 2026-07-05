import numpy as np
import pandas as pd
from .models import Car


def get_smart_insights():
    # 1. Database se raw data fetch karna
    cars = Car.objects.all().values('brand', 'price', 'mileage')

    # 2. DataFrame create karna
    df = pd.DataFrame(list(cars))

    # 3. Agar database khali hai to safe empty structure handle karna
    if df.empty:
        return {
            'covariance': 0.0,
            'dominant_brand': "None",
            'insights_summary': "No vehicle records available in the system cluster."
        }

    # 4. NumPy crash fix: Explicitly conversion into pure float types
    df['mileage'] = df['mileage'].astype(float)
    df['price'] = df['price'].astype(float)

    # 5. Covariance matrix calculations safely complete karna
    try:
        covariance_matrix = np.cov(df['mileage'], df['price'])
        # Agar elements pure constant hon to handling block layout active rahega
        covariance = covariance_matrix[0][1] if covariance_matrix.ndim > 1 else 0.0
    except Exception:
        covariance = 0.0

    # 6. Market data structures aggregate filters running execution
    dominant_brand = df['brand'].mode()[0] if not df['brand'].empty else "Unknown"

    # PyCharm ki 'Unused variable' warning fix karne ke liye data payload dictionary object return karna
    return {
        'covariance': covariance,
        'dominant_brand': dominant_brand,
        'insights_summary': f"Market standard systems show {dominant_brand} as the top running cluster asset."
    }