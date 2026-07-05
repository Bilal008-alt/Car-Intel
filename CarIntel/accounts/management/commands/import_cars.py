import pandas as pd
from django.core.management.base import BaseCommand
from accounts.models import Car
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Imports car data from cars.csv via Pandas'

    def handle(self, *args, **kwargs):
        file_path = 'cars.csv'
        self.stdout.write(self.style.SUCCESS('Reading Kaggle Dataset via Pandas...'))

        try:
            df = pd.read_csv(file_path)
            admin_user = User.objects.filter(is_superuser=True).first()

            for _, row in df.iterrows():
                Car.objects.create(
                    owner=admin_user,
                    brand=row['brand'],
                    model=row['model'],
                    year=int(row['year']),
                    mileage=int(row['mileage']),
                    fuel_type=row['fuel_type'],
                    transmission=row['transmission'],
                    price=int(row['price'])
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported Kaggle data! 🎉'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))