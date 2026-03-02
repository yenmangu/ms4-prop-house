from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalogue.models import Product
import cloudinary.uploader
import urllib.parse
import re
import requests
import time
from tqdm import tqdm

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

    def add_arguments(self, parser):
        """
        Defines the CLI arguments for the command.
        """
        # Add store_true action

        parser.add_argument(
            "--auto-find",
            action="store_true",
            help="Automatically find and upload images from Unsplash based on product name",
        )

    def clean_search_term(self, name):
        """
        Sanitizes the product name into a clean string for search engines.

        Removes parentheses, special characters, and 'noise' words (like 'pro' or 'v1')
        to ensure the search engine focuses on the actual object.

        Args:
            name (str): The raw product name from the database.

        Returns:
            str: A stripped, space-separated string of key nouns and adjectives.
        """
        # Remove anything inside parantheses (e.g. "(Blue)")
        text = re.sub(r"\(.*?\)", "", name)

        # Replace hyphens and underscore with spaces
        text = text.replace("-", " ").replace("_", " ")

        # Remove numbers and special chars
        text = re.sub(r"[^a-zA-Z\s]", "", text)

        # Remove 'noisy' terms that ruin image search
        noise_words = {"v1", "v2", "pro", "edition", "mnodel", "series"}
        words = [w for w in text.split() if w.lower() not in noise_words and len(w) > 2]

        # Join it back together and URL encode it
        clean_name = " ".join(words)
        return clean_name.strip()

    def is_valid_image_url(self, url):
        """
        Verifies if a URL leads to a valid, reachable image.

        Sends a HEAD request to check the status code (200) and ensures the
        Content-Type header starts with 'image/'.

        Args:
            url (str): The URL of the image to check.

        Returns:
            bool: True if the image is valid and accessible, False otherwise.
        """
        try:
            response = requests.head(
                url,
                timeout=5,
                allow_redirects=True,
            )

            is_ok = response.status_code == 200
            is_image = "image" in response.headers.get("Content-Type", "").lower()

            return is_ok and is_image
        except Exception:
            return False

    def optimise_search_term(self, clean_name):
        """
        Creates a 'Waterfall' list of search variations to maximize success.

        Generates attempts starting from the specific full name down to the
        broad primary noun and the most descriptive (longest) word.

        Args:
            clean_name (str): The output from clean_search_term.

        Returns:
            list: A unique list of URL-encoded search strings.
        """
        raw_name = clean_name.replace("%20", " ")
        words = raw_name.split()
        if not words:
            return ["product"]

        attempts = []

        # 1. Full cleaned name
        attempts.append(" ".join(words))

        # 2. Last two words
        if len(words) >= 2:
            attempts.append(" ".join(words[-2:]))

        # 3. Last word only (primary noun)
        attempts.append(words[-1])

        # 4. Longest word
        longest_word = max(words, key=len)
        attempts.append(longest_word)

        final_list = []

        for a in attempts:
            quoted = urllib.parse.quote(a)
            final_list.append(quoted)

        return list(dict.fromkeys(final_list))

    def handle(self, *args, **options):
        """
        The main execution logic for the management command.

        Iterates through all products, decides between 'Auto-find' mode
        (API search) or 'Local' mode (Direct upload), handles the Cloudinary
        handshake, and updates the database with secure URLs.
        """
        # Set catalogue folder name
        folder = "catalogue_seeds"

        # Detect if flag present
        auto_find = options["auto_find"]

        # Fetch all products from DB
        products = Product.objects.all()

        pbar = tqdm(products, desc="Seeding products", unit="product")

        self.stdout.write(f"Found {products.count()} items to process.")

        # for product in products:
        #     clean_name = self.clean_search_term(product.name)
        #     attempts = self.optimise_search_term(clean_name=clean_name)

        # self.stdout.write(f"PROD: {product.name} -> ATTEMPTS: {attempts}")

        # The loop
        for product in pbar:
            source = None

            try:
                if auto_find:

                    if "cloudinary" in str(product.featured_image):
                        continue

                    # Mode A - 'Lazy' automated search
                    clean_name = self.clean_search_term(product.name)
                    search_attempts = self.optimise_search_term(clean_name=clean_name)

                    success = False

                    for term in search_attempts:

                        sources = [
                            f"https://loremflickr.com/800/600/{term}",
                            f"https://source.unsplash.com/featured/?{term}",  # Try Unsplash again
                            f"https://api.duis.com/image?q={term}",  # Another backup
                            f"https://picsum.photos/seed/{product.id}/800/600",  # Pure random fallback
                        ]

                        for source_url in sources:

                            if self.is_valid_image_url(source_url):
                                source = source_url
                                success = True
                                break

                        if success:
                            break

                    if not success:
                        source = f"https://placehold.co/800x600.png?text={urllib.parse.quote(clean_name)}+Coming+Soon"
                        success = True
                        # Use pbar.write to avoid breaking the progress bar
                        pbar.write(
                            self.style.ERROR(
                                f"Could not find any image for {product.name}"
                            )
                        )

                        continue

                else:
                    # Mode B - 'Upload from local'
                    if (
                        "cloudinary" in str(product.featured_image)
                        or not product.featured_image
                    ):
                        continue
                    source = product.featured_image.path
                    success = True

                if success and source:
                    pbar.set_postfix({"item": product.name[:15]})
                    clean_filename = f"{slugify(product.name)}-{product.id}"

                    # 1. Prepare upload
                    upload_data = cloudinary.uploader.upload(
                        source,
                        folder=folder,
                        public_id=clean_filename,
                        overwrite=True,
                    )

                    # 2. Capture
                    cloudinary_url = upload_data.get("secure_url")

                    # 3. Update
                    # Change product image field to new url and save

                    product.featured_image = cloudinary_url
                    product.save()

            except Exception as e:
                pbar.write(self.style.ERROR(f"Failed to upload {product.name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
