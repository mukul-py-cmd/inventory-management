from rest_framework import permissions


class is_user_box_creator(permissions.BasePermission):
	message = 'You must be the owner of this box'

	def has_object_permission(self, request, view, obj):
		return obj.created_by == request.user