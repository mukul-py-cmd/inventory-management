from django.urls import path
from . import views
from .views import Box_list,My_Box_List,delete_box,create_box

urlpatterns = [
	path('', views.index, name = 'index'),
	path('boxes/<int:id>/',create_box.as_view(), name = 'update_box'),
	path('boxes/',create_box.as_view(), name = 'create_box'),	
	path('myboxes/',My_Box_List.as_view(), name = 'my_box_list'),
    path('myboxes/<int:id>/',delete_box.as_view(), name = 'delete_box'),
	path('box-list/',Box_list.as_view(), name = 'box_list'),


]

