from django.core.management.base import BaseCommand
from catalogue.models import Product
import cloudinary.uploader

# Phase 1 - Tools - identify the tools needed
# BaseCommand - parent class to handle terminal stuff
# Product - class to manipulate data
# cloudinary.uploader - delivery driver to upload image into cloudinary account

# Phase 2 - Flow - loop to iterate total product amount of times.
# write one process and tell Python to repeat


class Command(BaseCommand):
    help = "A short description for the --help flag"

    def handle(self, *args, **options):

        # Fetch all products from DB
        products = Product.objects.all()
        self.stdout.write(f"Found {products.count()} items to process.")

        # The loop
        for product in products:
            self.stdout.write(f"Currently processing:  {product.name}")

        pass
