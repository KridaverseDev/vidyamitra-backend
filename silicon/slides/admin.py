from django.contrib import admin

from .models import Favorite, Presentation, Slides

# Register your models here.

admin.site.register(Presentation)
admin.site.register(Slides)
admin.site.register(Favorite)
