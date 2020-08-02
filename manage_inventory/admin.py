from django.contrib import admin
from .models import Box

# Register your models here.
class BoxAdmin(admin.ModelAdmin):

	#to override area, volume and user when saved using django-admin
	def save_model(self, request, obj, form, change):
		if obj.length and obj.breadth and obj.height:
			obj.area = round(obj.length*obj.breadth,3)
			obj.volume = round(obj.length*obj.breadth*obj.height,3)
		if not change:
			obj.created_by = request.user       
		super().save_model(request, obj, form, change) 



admin.site.register(Box, BoxAdmin)
