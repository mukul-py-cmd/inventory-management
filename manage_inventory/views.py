from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import BoxSerializer,staff_BoxSerializer,Box_create_Serializer
from .models import Box
from rest_framework import generics, status
from rest_framework.permissions import (
	AllowAny,
	IsAuthenticated,
	IsAdminUser,
	IsAuthenticatedOrReadOnly
	)
from .permissions import is_user_box_creator
from rest_framework.views import APIView
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime,date, timedelta

A1 = 5000
V1 = 5000
L1 = 100
L2 = 50



@api_view(['GET'])
def index(request):
	content = {

	"get_list_of_all_boxes": {
	"url" : "box-list/?length_more_than=5&volume_less_than=9",
	"authorization" : "Logged-in",
	"filter_by" :  [
	"length_more_than", 
	"length_less_than",
	"breadth_more_than", 
	"breadth_less_than",
	"height_more_than", 
	"height_less_than",
	"area_more_than", 
	"area_less_than", 
	"volume_more_than",
	"volume_less_than", 
	"username", 
	"before_date",
	"after_date",
	]
	},
	"get_list_of_all_my_boxes": {
	"url" : "myboxes/?length_more_than=5&volume_less_than=9",
	"authorization" : "Logged-in",
	"filter_by" :  [
	"length_more_than", 
	"length_less_than",
	"breadth_more_than", 
	"breadth_less_than",
	"height_more_than", 
	"height_less_than",
	"area_more_than", 
	"area_less_than", 
	"volume_more_than",
	"volume_less_than", 
	]
	},
	"add new box": {
	"url" : "boxes/",
	"authorization" : "Logged-in, Staff-User",
	"post request format" : {
	"length" : 1,
	"height" : 5.33,
	"breadth" : 6
	}
	},
	"update box": {
	"url" : "boxes/id/",
	"authorization" : "Logged-in, Staff-User",
	"put request format" : {
	"length" : 1,
	"breadth" : 6
	}
	},
	"delete box": {
	"url" : "myboxes/id/",
	"authorization" : "Logged-in, Staff-User, box_creator_permission"
	}


	}
	return Response(content)


# create and update inventory after authorising and checking constraints
class create_box(APIView):
	permission_classes = [IsAuthenticated,IsAdminUser]

	def post(self,request):
		data = request.data
		try:
			data = self.create_data(data)
		except Exception as e:
			return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
						
		serializer = Box_create_Serializer(data=data)
		if serializer.is_valid(raise_exception=True):
			try:
				self.check_constraints(request,serializer.validated_data)
			except Exception as e:
				return Response(str(e) , status=status.HTTP_400_BAD_REQUEST)
			
			serializer.save(created_by = request.user)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self,request,id):
		data = request.data
		box = Box.objects.get(id = id)
		data = self.create_data(data,box)
		serializer = Box_create_Serializer(instance = box,data=data)
		if serializer.is_valid(raise_exception=True):
			try:
				self.check_constraints(request,serializer.validated_data,box)
			except Exception as e:
				return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
			serializer.save(created_by = box.created_by)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def create_data(self,data,box= None):
		try:
			length = data.get('length')
			breadth = data.get('breadth')
			height = data.get('height')
			if length is None:
				length = box.length
				data['length'] = length
			if breadth is None:
				breadth = box.breadth
				data['breadth'] = breadth
			if height is None:
				height = box.height
				data['height'] = height
			length = Decimal(length)
			breadth = Decimal(breadth)
			height = Decimal(height)
			area = length*breadth
			volume = length*height*breadth
			area = round(area, 3)
			volume = round(volume, 3)
			data['area'] =area
			data['volume'] = volume

			return data
		except Exception as e:
			raise Exception("Please check the height, length, and breadth again!")
		

	def check_constraints(self,request,validated_data,obj = None):
		instance_count = 1
		instance_area = 0
		instance_vol = 0
		if obj:
			instance_count = 0
			instance_area = obj.area
			instance_vol = obj.volume

		total_area = Box.objects.aggregate(total_area = Sum('area')).get('total_area')
		total_area = 0 if ( total_area is None) else total_area
		if ((Box.objects.count() + instance_count) * A1) < (total_area + validated_data.get('area') - instance_area):
			raise Exception("Can't add: total average area exceeded than allowed")

		total_vol = Box.objects.filter(created_by = request.user).aggregate(total_vol = Sum('volume')).get('total_vol')
		total_vol = 0 if ( total_vol is None) else total_vol
		if ((Box.objects.filter(created_by = request.user).count() + instance_count) * V1 )< (total_vol + validated_data.get('volume')-instance_vol):
			raise Exception("Can't add: total average volume exceeded than allowed for you")
		
		today = date.today()
		start_date = today - timedelta(days=today.weekday())
		if (Box.objects.filter(created_on__range=(start_date, today)).count() +  instance_count) > L1:
			raise Exception("Can't add: weekly limit to add exceeded")

		if (Box.objects.filter(created_by = request.user).filter(created_on__range=(start_date, today)).count() + instance_count )> L2:
			raise Exception("Can't add: your weekly limit to add exceeded")



			


# gives list of all boxes after applying filters and  if user is authenticated
class Box_list(APIView):
	permission_classes = [IsAuthenticated]

	def get(self,request):
		box_list = self.create_query(request)
		if request.user.is_staff:
			serializer = staff_BoxSerializer(box_list, many=True)
		else:
			serializer = BoxSerializer(box_list, many=True)
		return Response(serializer.data)

	def create_query(self,request):
		queryset = Box.objects.all()
		length_more_than = request.query_params.get('length_more_than')
		length_less_than = request.query_params.get('length_less_than')
		breadth_more_than = request.query_params.get('breadth_more_than')
		breadth_less_than = request.query_params.get('breadth_less_than')
		height_more_than = request.query_params.get('height_more_than')
		height_less_than = request.query_params.get('height_less_than')
		area_more_than = request.query_params.get('area_more_than')
		area_less_than = request.query_params.get('area_less_than')
		volume_more_than = request.query_params.get('volume_more_than')
		volume_less_than = request.query_params.get('volume_less_than')
		username = request.query_params.get('username')
		before_date = request.query_params.get('before_date')
		after_date = request.query_params.get('after_date')

		if length_more_than:
		    queryset = queryset.filter(length__gt=length_more_than)
		if length_less_than:
		    queryset = queryset.filter(length__lt=length_less_than)
		if breadth_more_than:
		    queryset = queryset.filter(breadth__gt=breadth_more_than)
		if breadth_less_than:
		    queryset = queryset.filter(breadth__lt=breadth_less_than)
		if height_more_than:
		    queryset = queryset.filter(height__gt=height_more_than)
		if height_less_than:
		    queryset = queryset.filter(height__lt=height_less_than)
		if area_more_than:
		    queryset = queryset.filter(area__gt=area_more_than)
		if area_less_than:
		    queryset = queryset.filter(area__lt=area_less_than)
		if volume_more_than:
		    queryset = queryset.filter(volume__gt=volume_more_than)
		if volume_less_than:
		    queryset = queryset.filter(volume__lt=volume_less_than)
		if username:
		    queryset = queryset.filter(created_by = username)
		if before_date:
			before_date = datetime.strptime(before_date, '%Y-%m-%d').date()
			queryset = queryset.filter(created_on__lt=before_date)
		if after_date:
			after_date = datetime.strptime(after_date, '%Y-%m-%d').date()
			queryset = queryset.filter(created_on__gt=after_date)
		
		return queryset



# gives list of all boxes of logged in staff user after applying filters 
class My_Box_List(APIView):
	permission_classes = [IsAuthenticated,IsAdminUser]

	def get(self,request):
		box_list = self.create_query(request)
		print(box_list)
		serializer = BoxSerializer(box_list, many=True)
		return Response(serializer.data)

	def create_query(self,request):
		queryset = Box.objects.all()
		length_more_than = request.query_params.get('length_more_than')
		length_less_than = request.query_params.get('length_less_than')
		breadth_more_than = request.query_params.get('breadth_more_than')
		breadth_less_than = request.query_params.get('breadth_less_than')
		height_more_than = request.query_params.get('height_more_than')
		height_less_than = request.query_params.get('height_less_than')
		area_more_than = request.query_params.get('area_more_than')
		area_less_than = request.query_params.get('area_less_than')
		volume_more_than = request.query_params.get('volume_more_than')
		volume_less_than = request.query_params.get('volume_less_than')

		if length_more_than:
		    queryset = queryset.filter(length__gt=length_more_than)
		if length_less_than:
		    queryset = queryset.filter(length__lt=length_less_than)
		if breadth_more_than:
		    queryset = queryset.filter(breadth__gt=breadth_more_than)
		if breadth_less_than:
		    queryset = queryset.filter(breadth__lt=breadth_less_than)
		if height_more_than:
		    queryset = queryset.filter(height__gt=height_more_than)
		if height_less_than:
		    queryset = queryset.filter(height__lt=height_less_than)
		if area_more_than:
		    queryset = queryset.filter(area__gt=area_more_than)
		if area_less_than:
		    queryset = queryset.filter(area__lt=area_less_than)
		if volume_more_than:
		    queryset = queryset.filter(volume__gt=volume_more_than)
		if volume_less_than:
		    queryset = queryset.filter(volume__lt=volume_less_than)
		queryset = queryset.filter(created_by = request.user)
		return queryset



#deletes the box after checking authentication and authorization	
class delete_box(APIView):
	permission_classes = [IsAdminUser,is_user_box_creator]

	def delete(self,request,id):
		box = get_object_or_404(Box, id = id)
		self.check_object_permissions(self.request, box)
		box.delete()
		return Response({"message" : "successfully deleted box {0}".format(id)})



"""
# Create your views here.
@api_view(['GET', 'POST'])
def list_all_boxes(request):
	spi = {
	"name":"Mukul",
	"age":10

	}
	return Response(spi)


@api_view(['GET'])
def get_box_list(request):
	box_list = Box.objects.all()
	if request.user.is_staff:
		serializer = staff_BoxSerializer(box_list, many=True)
	else:
		serializer = BoxSerializer(box_list, many=True)
	return Response(serializer.data)
"""
"""
@api_view(['GET'])
def get_my_box_list(request,id = None):
	if request.method == 'GET':
		box_list = Box.objects.filter(created_by = request.user)
		serializer = BoxSerializer(box_list, many=True)
		return Response(serializer.data)
"""
"""
@api_view(['DELETE'])
def delete_box(request,id = None):
	try:
	    box = Box.objects.get(id = id)
	except Box.DoesNotExist:
	    return HttpResponse(status=404)
	if box.created_by == request.user:	    
		box.delete()
		spi = {
		"message":"successfully deleted",
		"box_id":id
		}
		return Response(spi)
	return Response({"message" : "permission denied"})

"""

