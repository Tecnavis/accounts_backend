from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.models import Category,Service
from .serializers import CategorySerializer,ServiceSerializer
from main.management.commands.create_roles_and_permissions import IsMainAdmin,IsSecondaryAdmin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all() 
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def category_create(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      


@api_view(['GET'])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([AllowAny])
def category_update(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def category_delete(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



# -------------------------------------------------------------------------------------------


# list services by category
@api_view(['GET'])
@permission_classes([AllowAny])
def services(request):
    services = Service.objects.all()
    print(services,"data") 
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def service_list(request, category_id=None):
    if category_id:
        
        category = Category.objects.get(id=category_id)
        services = Service.objects.filter(category=category)
    else:
        services = Service.objects.all()

    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


# Create a service under a specific category
@api_view(['POST'])
@permission_classes([AllowAny])
def create_service(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    data['category'] = category.id  

    serializer = ServiceSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @permission_classes([IsSecondaryAdmin,IsMainAdmin])

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_service(request, category_id, service_id):
    try:
        new_category_id = request.data.get("category_id", category_id)  
        category = Category.objects.get(id=new_category_id)
    except Category.DoesNotExist:
        return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'detail': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

    updated_data = request.data.copy()
    updated_data['category'] = category.id 
    
    serializer = ServiceSerializer(service, data=updated_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return Response({'detail': 'Service deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response({'detail': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
