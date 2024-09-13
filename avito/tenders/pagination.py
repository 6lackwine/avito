from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    """ Класс для создания пагинации """

    def get_paginated_response(self, data: dict) -> Response:
        """ Функция для получения пагинации """
        return Response(data)
