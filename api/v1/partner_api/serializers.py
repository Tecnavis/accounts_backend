from rest_framework import serializers
from partner.models import PartnerProfile, PartnerType
from users.models import CustomUser

class PartnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerProfile
        fields = "__all__"
        read_only_fields = ["profile_id", "created_by", "updated_by", "created_at", "updated_at"]

    def validate_partner_type(self, value):
        """Ensure partner_type is either 'customer' or 'vendor'."""
        valid_types = {choice[0] for choice in PartnerType.CHOICES}
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid partner_type. Choose from {valid_types}.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)
