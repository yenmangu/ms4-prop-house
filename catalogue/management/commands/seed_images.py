from django.core.management.base import BaseCommand
from catalogue.models import Product
import cloudinary.uploader

# Phase 1 identify the tools needed
# BaseCommand - parent class to handle terminal stuff
# Product - class to manipulate data
# cloudinary.uploader - delivery driver to upload image into cloudinary account


class Command(BaseCommand):
    help = "A short description for the --help flag"

    def handle(self, *args, **options):
        pass
