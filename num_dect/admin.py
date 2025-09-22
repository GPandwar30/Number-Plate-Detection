from django.contrib import admin
from num_dect . models import ImageUpload
# Register your models here.
class ImageUploadAdmin(admin.ModelAdmin):
    list_ = ['image','uploaded_at']

admin.site.register(ImageUpload, ImageUploadAdmin)