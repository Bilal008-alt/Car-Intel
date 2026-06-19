import json
import pandas as pd
from django.shortcuts import render
from django.db.models import Avg, Count

# NOTE FOR MEMBER 4:
# Update this import once Member 2 confirms the actual app name their
# Car model lives in (per their card it's likely "cars" or "listings").
from cars.models import Car


def charts_dashboard(request):
    """
    Renders the 5 required Chart.js visualizations for CarIntel.

    Assumes the Car model has these fields (per M2-P1 card):
        brand, model, year, mileage, fuel_type, transmission, price
    """

    # ---- Chart 1: Bar Chart — Average price by brand ----
    brand_qs = (
        Car.objects.values('brand')
        .annotate(avg_price=Avg('price'))
        .order_by('-avg_price')[:10]  # top 10 brands keeps the chart readable
    )
    brand_labels = [row['brand'] for row in brand_qs]
    brand_prices = [round(float(row['avg_price']), 2) for row in brand_qs]

    # ---- Chart 2: Pie Chart — Fuel type distribution ----
    fuel_qs = Car.objects.values('fuel_type').annotate(count=Count('id'))
    fuel_labels = [row['fuel_type'] for row in fuel_qs]
    fuel_counts = [row['count'] for row in fuel_qs]

    # ---- Chart 3: Line Chart — Average price by manufacturing year ----
    year_qs = (
        Car.objects.values('year')
        .annotate(avg_price=Avg('price'))
        .order_by('year')
    )
    year_labels = [row['year'] for row in year_qs]
    year_prices = [round(float(row['avg_price']), 2) for row in year_qs]

    # ---- Chart 4: Histogram — Price distribution (binned with Pandas) ----
    # Chart.js has no native histogram type, so we bucket prices into 10
    # ranges server-side and render them as a bar chart.
    prices = list(Car.objects.values_list('price', flat=True))
    hist_labels, hist_counts = [], []
    if prices:
        df = pd.DataFrame({'price': prices})
        bins = pd.cut(df['price'], bins=10)
        hist_series = bins.value_counts().sort_index()
        hist_labels = [
            f"{int(interval.left):,} - {int(interval.right):,}"
            for interval in hist_series.index
        ]
        hist_counts = hist_series.values.tolist()

    # ---- Chart 5: Scatter Plot — Mileage vs Price ----
    scatter_qs = Car.objects.values('mileage', 'price')
    scatter_data = [
        {'x': row['mileage'], 'y': float(row['price'])}
        for row in scatter_qs
    ]

    context = {
        'brand_labels': json.dumps(brand_labels),
        'brand_prices': json.dumps(brand_prices),
        'fuel_labels': json.dumps(fuel_labels),
        'fuel_counts': json.dumps(fuel_counts),
        'year_labels': json.dumps(year_labels),
        'year_prices': json.dumps(year_prices),
        'hist_labels': json.dumps(hist_labels),
        'hist_counts': json.dumps(hist_counts),
        'scatter_data': json.dumps(scatter_data),
        'total_cars': len(prices),
    }
    return render(request, 'visualizations/charts.html', context)
