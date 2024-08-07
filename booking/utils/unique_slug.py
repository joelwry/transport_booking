
from django.utils.text import slugify

def generate_unique_slug(instance, slug):
    """
    To Generate a unique slug for a given model instance.
    """
    model = instance.__class__
    unique_slug = slug
    extension = 1
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{extension}"
        extension += 1
    return unique_slug