import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Max, Min
from django.core.paginator import Paginator
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from .models import Car
from .forms import CustomSignupForm, CustomLoginForm, CarForm
from .utils import get_smart_insights


# === MEMBER 1: AUTHENTICATION VIEWS ===
def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomSignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')


# === MEMBER 3: DASHBOARD LANDING & METRICS ===
@login_required
def profile_view(request):
    metrics = Car.objects.aggregate(
        total=Count('id'),
        avg_price=Avg('price'),
        peak_val=Max('price'),
        lowest_val=Min('price')
    )
    return render(request, 'accounts/profile.html', {'metrics': metrics})


# === MEMBER 3: SEARCH LOGIC & PAGINATION ===
@login_required
def car_search(request):
    cars = Car.objects.all()

    brand = request.GET.get('brand', '')
    fuel = request.GET.get('fuel', '')
    transmission = request.GET.get('transmission', '')
    sort = request.GET.get('sort', '')

    if brand:
        cars = cars.filter(brand__icontains=brand)
    if fuel:
        cars = cars.filter(fuel_type__iexact=fuel)
    if transmission:
        cars = cars.filter(transmission__iexact=transmission)

    if sort == 'low':
        cars = cars.order_by('price')
    elif sort == 'high':
        cars = cars.order_by('-price')

    paginator = Paginator(cars, 15)  # 15 Cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/search.html', {'page_obj': page_obj})


# === MEMBER 3: EXPORT FILTERED SEARCH TO CSV ===
@login_required
def export_cars_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_cars.csv"'

    writer = csv.writer(response)
    writer.writerow(['Brand', 'Model', 'Year', 'Mileage', 'Fuel Type', 'Transmission', 'Price'])

    cars = Car.objects.all()
    # Filter apply jo dynamic page pe the
    if request.GET.get('brand'): cars = cars.filter(brand__icontains=request.GET.get('brand'))
    if request.GET.get('fuel'): cars = cars.filter(fuel_type__iexact=request.GET.get('fuel'))
    if request.GET.get('transmission'): cars = cars.filter(transmission__iexact=request.GET.get('transmission'))

    for car in cars:
        writer.writerow([car.brand, car.model, car.year, car.mileage, car.fuel_type, car.transmission, car.price])

    return response


# === MEMBER 2: CRUD CLASS BASED VIEWS WITH OWNER PROTECTION ===
class CarDetailView(LoginRequiredMixin, DetailView):
    model = Car
    template_name = 'accounts/car_detail.html'


class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'accounts/car_form.html'
    success_url = reverse_lazy('car_search')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'accounts/car_form.html'
    success_url = reverse_lazy('car_search')

    def test_func(self):
        car = self.get_object()
        return car.owner == self.request.user


class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Car
    template_name = 'accounts/car_confirm_delete.html'
    success_url = reverse_lazy('car_search')

    def test_func(self):
        car = self.get_object()
        return car.owner == self.request.user


# === MEMBER 4: CHART.JS GRAPH DATA STREAMS & DATA ANALYTICS ===
@login_required
def insights_view(request):
    # Complex String Insights from Pandas Utility
    pandas_insights = get_smart_insights()

    # Chart 1 Data (Avg cost per brand)
    brand_data = Car.objects.values('brand').annotate(avg_p=Avg('price'))
    # Chart 2 Data (Fuel Types Distribution)
    fuel_data = Car.objects.values('fuel_type').annotate(count=Count('id'))
    # Chart 3 Data (listings grouped by year)
    year_data = Car.objects.values('year').annotate(avg_p=Avg('price')).order_by('year')
    # Chart 4 & 5 Metrics
    all_cars = Car.objects.all().values('price', 'mileage')

    context = {
        'insights': pandas_insights,
        'brand_labels': [b['brand'] for b in brand_data],
        'brand_prices': [float(b['avg_p']) for b in brand_data],
        'fuel_labels': [f['fuel_type'] for f in fuel_data],
        'fuel_counts': [f['count'] for f in fuel_data],
        'year_labels': [y['year'] for y in year_data],
        'year_prices': [float(y['avg_p']) for y in year_data],
        'scatter_data': [{'x': c['mileage'], 'y': c['price']} for c in all_cars],
        'prices_raw': [c['price'] for c in all_cars]
    }
    return render(request, 'accounts/insights.html', context)