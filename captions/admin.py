from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from django.contrib import admin
from .models import UploadedImage

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'caption')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;"/>', obj.image.url)
        return ""
    preview.short_description = "Preview"
