from django_filters import rest_framework as filters

from .models import Tenders


class TenderFilter(filters.FilterSet):
    """ Класс для фильтрации тендеров """
    class Meta:
        model = Tenders
        fields = ["filterServiceType"]