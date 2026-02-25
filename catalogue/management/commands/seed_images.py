from django.core.management.base import BaseCommand
from catalogue.models import Product
import cloudinary.uploader

# Phase 1 - Tools - identify the tools needed
# BaseCommand - parent class to handle terminal stuff
# Product - class to manipulate data
# cloudinary.uploader - delivery driver to upload image into cloudinary account

# Phase 2 - Flow - loop to iterate total product amount of times.
# write one process and tell Python to repeat


# Phase 3-4 - Handshake/Preparation - tell Cloudinary where the image is located
# Pass this path to the uploader
# Take response with new URL and set the product image to the new URL
## Wrap all this in try..except block to ensure graceful failure.
class Command(BaseCommand):
    help = "A short description for the --help flag"

    def handle(self, *args, **options):

        # Fetch all products from DB
        products = Product.objects.all()
        self.stdout.write(f"Found {products.count()} items to process.")

        # The loop
        for product in products:
            # Check product actually has image

            if not product.image:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {product.name}: No image found")
                )
                continue

            try:
                # 1. Upload
                upload_data = cloudinary.uploader.upload(
                    product.image.path,
                    folder="catalogue_seeds",
                )

                # 2. Capture
                cloudinary_url = upload_data.get("secure_url")

                # 3. Update
                # Change product image field to new url and save

                product.image = cloudinary_url
                product.save()

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully uploaded {product.name}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to upload {product.name}: {e}")
                )

            self.stdout.write(f"Currently processing:  {product.name}")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
