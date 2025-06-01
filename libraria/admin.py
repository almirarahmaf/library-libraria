from django.contrib import admin

# Register your models here.
from .models import Profile, category, booklist, review_user, borrowing

admin.site.register(Profile)
admin.site.register(category)
admin.site.register(booklist)
admin.site.register(review_user)
admin.site.register(borrowing)