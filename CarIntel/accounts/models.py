from django.db import models
from django.contrib.auth.models import User


class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    # 📸 Nayi Line: Uploaded image save karne ke liye (null=True taake purana data crash na ho)
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model}"