"""
用户视图
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


class UserMeView(APIView):
    """
    当前用户 API
    通过请求头 X-Device-ID 识别用户
    """

    def get_device_id(self, request):
        """获取设备ID"""
        device_id = request.headers.get("X-Device-ID")
        if not device_id:
            return None, Response(
                {"detail": "缺少 X-Device-ID 请求头"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return device_id, None

    def get(self, request):
        """获取当前用户信息"""
        device_id, error = self.get_device_id(request)
        if error:
            return error
        
        try:
            user = User.objects.get(device_id=device_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        """更新当前用户信息"""
        device_id, error = self.get_device_id(request)
        if error:
            return error
        
        try:
            user = User.objects.get(device_id=device_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateView(APIView):
    """
    创建用户 API
    """

    def post(self, request):
        """创建用户"""
        device_id = request.headers.get("X-Device-ID")
        if not device_id:
            return Response(
                {"detail": "缺少 X-Device-ID 请求头"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(device_id=device_id).exists():
            return Response(
                {"detail": "用户已存在"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create(device_id=device_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserCookedRecipeView(APIView):
    """
    记录制作食谱 API
    """

    def post(self, request, recipe_id):
        """记录制作一次食谱"""
        device_id = request.headers.get("X-Device-ID")
        if not device_id:
            return Response(
                {"detail": "缺少 X-Device-ID 请求头"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user, _ = User.objects.get_or_create(device_id=device_id)
        
        # 更新制作次数
        recipe_key = str(recipe_id)
        cooked = user.cooked_recipes or {}
        cooked[recipe_key] = cooked.get(recipe_key, 0) + 1
        user.cooked_recipes = cooked
        user.save(update_fields=["cooked_recipes"])
        
        return Response({
            "recipe_id": recipe_id,
            "count": cooked[recipe_key]
        })
