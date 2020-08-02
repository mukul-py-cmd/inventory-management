from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Box(models.Model):
	length = models.DecimalField(max_digits=6, decimal_places=3)
	breadth = models.DecimalField(max_digits=6, decimal_places=3)
	height = models.DecimalField(max_digits=6, decimal_places=3)
	area = models.DecimalField(max_digits=10, decimal_places=3,blank=True)
	volume = models.DecimalField(max_digits=13, decimal_places=3,blank=True)
	created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True)
	created_on = models.DateField(auto_now_add=True)
	updated_on = models.DateField(auto_now=True)

	
	# def save(self,*args,**kwargs):
	# 	if self.length and self.breadth and self.height:
	# 		self.area = round(self.length*self.breadth)
	# 		self.volume = round(self.length*self.breadth*self.height)
			
	# 	super(Box,self).save(*args,**kwargs)



