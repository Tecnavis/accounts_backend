from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from partner.models import PartnerProfile
from .serializers import PartnerProfileSerializer
from rest_framework.permissions import AllowAny

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_partner(request):
    serializer = PartnerProfileSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_partner_by_id(request, id):    
    partner = PartnerProfile.objects.get(id=id)
    print(partner,"partner")
    serializer = PartnerProfileSerializer(partner)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_partners(request):
    partner_type = request.GET.get("partner_type")
    if partner_type in ["customer", "vendor"]:
        partners = PartnerProfile.objects.filter(partner_type=partner_type)
    else:
        partners = PartnerProfile.objects.all()
    paginator = Paginator(partners, 20)  
    page = request.GET.get("page", 1)
    partners_page = paginator.page(page)

    serializer = PartnerProfileSerializer(partners_page, many=True)
    return Response({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": int(page),
        "results": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_partner(request, pk):
    partner = get_object_or_404(PartnerProfile, pk=pk)
    serializer = PartnerProfileSerializer(partner)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_partner(request, id):
    partner = get_object_or_404(PartnerProfile, id=id)
    serializer = PartnerProfileSerializer(partner, data=request.data, partial=True, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_partner(request, id):
    partner = get_object_or_404(PartnerProfile, id=id)
    partner.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)  
