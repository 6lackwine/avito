from rest_framework import serializers

from .models import Tenders


class TenderSerializer(serializers):
    class Meta:
        model = Tenders
        fields = ["tenderId", "tenderName", "tenderDescription", "tenderServiceType", "tenderStatus",
                  "tenderVersion", "created_at"]