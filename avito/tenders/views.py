from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .filters import TenderFilter
from .models import Tenders, Employee, Bids, Organization, OrganizationResponsible, Reviews
from .pagination import CustomPagination
from .serializers import TenderSerializer


class PingAPIView(APIView):
    """ Класс для проверки доступности сервера """

    def get(self, request: Request) -> Response:
        try:
            return Response(status=HTTP_200_OK, data="ok")
        except Exception:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


class TendersAPIView(ListAPIView):
    """ Класс для получения списка тендеров """
    pagination_class = CustomPagination
    serializer_class = TenderSerializer
    filterset_class = TenderFilter

    # filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        try:
            service_types: str = self.request.query_params.get('service_type')
            queryset = Tenders.objects.all()

            if service_types:
                queryset = queryset.filter(tenderServiceType=service_types)
            return queryset
        except Exception as e:
            return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                            status=HTTP_400_BAD_REQUEST)


class TendersNewAPIView(APIView):
    """ Класс для создания нового тендера """

    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        request_username = request.data.get("creatorUsername")
        try:
            db_username = Employee.objects.get(username=request_username).username
        except ObjectDoesNotExist:
            db_username = None
        try:
            if request.method == "POST":
                if request_username == db_username:
                    try:
                        tender = Tenders.objects.create(
                            tenderName=request.data.get("name"),
                            tenderDescription=request.data.get("description"),
                            tenderServiceType=request.data.get("serviceType"),
                            organizationId=request.data.get("organizationId"),
                            creatorUsername=request.data.get("creatorUsername")
                        )
                        response_data = {
                            "id": tender.tenderId,
                            "name": tender.tenderName,
                            "description": tender.tenderDescription,
                            "service_type": tender.tenderServiceType,
                            "status": tender.tenderStatus,
                            "version": tender.tenderVersion,
                            "createdAt": tender.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        }
                        return Response(status=HTTP_200_OK, data=response_data)
                    except Exception as e:
                        return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                        status=HTTP_400_BAD_REQUEST)
                elif db_username is None:
                    reason = {"reason": "Пользователь не существует или некорректен"}
                    return Response(status=HTTP_401_UNAUTHORIZED, data=reason)
        except Exception as e:
            reason = {"reason": f"Ошибка при создании тендера: {str(e)}"}
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR, data=reason)


class TendersStatusAPIView(APIView):
    """ Класс для получения и изменения текущего статуса """

    # permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request: Request, tenderId: str) -> Response:
        user = request.query_params.get("username")
        try:
            tender = Tenders.objects.get(tenderId=tenderId)
            if user == tender.creatorUsername:
                return Response(data=tender.status, status=HTTP_200_OK)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)

        except Tenders.DoesNotExist:
            return Response(data={"reason": "Тендер не найден"},
                            status=HTTP_404_NOT_FOUND)

    def put(self, request: Request, tenderId: str) -> Response:
        user = request.query_params.get("username")
        try:
            status = Tenders.objects.get(tenderId=tenderId)
            if user == status.creatorUsername:
                try:
                    new_status = request.query_params["status"]
                    status.tenderStatus = new_status
                    status.tenderVersion += 1
                    status.save()

                    response_data = {
                        "id": status.tenderId,
                        "name": status.tenderName,
                        "description": status.tenderDescription,
                        "status": status.tenderStatus,
                        "serviceType": status.tenderServiceType,
                        "version": status.tenderVersion,
                        "createdAt": status.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    }
                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Tenders.DoesNotExist:
            return Response(data={"reason": "Тендер не найден"},
                            status=HTTP_404_NOT_FOUND)


class TendersEditAPIView(APIView):
    """ Класс для редактирования тендера """

    # permission_classes = [permissions.IsAuthenticated, ]

    def patch(self, request: Request, tenderId: str) -> Response:
        user = request.query_params.get("username")
        try:
            tender = Tenders.objects.get(tenderId=tenderId)
            if user == tender.creatorUsername:
                try:
                    if "name" in request.data:
                        tender.tenderName = request.data.get("name")

                    if "description" in request.data:
                        tender.tenderDescription = request.data.get("description")

                    if "serviceType" in request.data:
                        tender.tenderServiceType = request.data.get("serviceType")

                    tender.version += 1

                    tender.save()

                    response_data = {
                        "id": tender.tenderId,
                        "name": tender.tenderName,
                        "description": tender.tenderDescription,
                        "status": tender.tenderStatus,
                        "serviceType": tender.tenderServiceType,
                        "version": tender.tenderVersion,
                        "createdAt": tender.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }
                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Tenders.DoesNotExist:
            return Response(data={"reason": "Тендер не найден"},
                            status=HTTP_404_NOT_FOUND)


class TendersRollbackVersionAPIView(APIView):
    """ Класс для отката версии тендера """

    # permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request: Request, tenderId: str, version: int):
        user = request.query_params.get("username")
        try:
            tender = Tenders.objects.get(tenderId=tenderId)
            if user == tender.creatorUsername:
                try:

                    tender.tenderVersion = version
                    tender.save()

                    response_data = {
                        "id": tender.tenderId,
                        "name": tender.tenderName,
                        "description": tender.tenderDescription,
                        "status": tender.tenderStatus,
                        "serviceType": tender.tenderServiceType,
                        "version": tender.tenderVersion,
                        "createdAt": tender.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Tenders.DoesNotExist:
            return Response(data={"reason": "Тендер не найден"},
                            status=HTTP_404_NOT_FOUND)


class UserTendersListAPIView(APIView):
    """ Класс для получения списка тендеров текущего пользователя """

    def get(self, request):
        user = request.query_params.get("username")
        limit = int(request.GET.get('limit', 5))
        offset = int(request.GET.get('offset', 0))

        tenders = Tenders.objects.filter(creatorUsername=user).order_by('tenderName')[offset:offset + limit]
        if not tenders:
            return Response(data={"reason": "Пользователь не существует или некорректен."},
                            status=HTTP_401_UNAUTHORIZED)

        serialized_tenders = []
        for tender in tenders:
            serialized_tender = {
                "id": tender.tenderId,
                "name": tender.tenderName,
                "description": tender.tenderDescription,
                "status": tender.tenderStatus,
                "serviceType": tender.tenderServiceType,
                "version": tender.tenderVersion,
                "createdAt": tender.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            serialized_tenders.append(serialized_tender)
        return Response(serialized_tenders, status=HTTP_200_OK)


class BidsNewAPIView(APIView):
    """ Класс для создания нового предложения """

    # permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request: Request):
        try:
            user = Employee.objects.get(id=request.data.get("authorId"))
        except Employee.DoesNotExist:
            reason = {
                "reason": "Пользователь не существует или некорректен"
            }
            return Response(status=HTTP_401_UNAUTHORIZED, data=reason)

        try:
            tender = Tenders.objects.get(tenderId=request.data.get("tenderId"))
            organization = OrganizationResponsible.objects.get(user_id=user)

            bids = Bids.objects.create(
                bidName=request.data.get("name"),
                bidDescription=request.get("description"),
                tenderId=tender,
                authorType=request.data.get("authorType"),
                organizationId=organization.organization_id,
                authorId=user
            )

            response_data = {
                "id": bids.bidId,
                "name": bids.bidName,
                "status": bids.bidStatus,
                "authorType": bids.bidAuthorType,
                "authorId": bids.bidAuthorId.id,
                "version": bids.bidVersion,
                "createdAt": bids.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            return Response(status=HTTP_200_OK, data=response_data)

        except Tenders.DoesNotExist:
            return Response(data={"reason": "Тендер не найден"},
                            status=HTTP_404_NOT_FOUND)


class BidsMyAPIView(APIView):
    """ Класс для получения списка предложений пользователя  """

    def get(self, request: Request) -> Response:
        user = request.query_params.get("username")
        limit = int(request.GET.get('limit', 5))
        offset = int(request.GET.get('offset', 0))
        my_user = Employee.objects.get(username=user)

        bids = Bids.objects.filter(authorId=my_user.id).order_by('bidName')[offset:offset + limit]
        if not bids:
            return Response(data={"reason": "Пользователь не существует или некорректен."},
                            status=HTTP_401_UNAUTHORIZED)

        serialized_tenders = []
        for bid in bids:
            serialized_tender = {
                "id": bid.bidId,
                "name": bid.bidName,
                "status": bid.bidStatus,
                "authorType": bid.bidAuthorType,
                'authorId': bid.bidAuthorId.id,
                "version": bid.bidVersion,
                "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            serialized_tenders.append(serialized_tender)

        return Response(serialized_tenders, status=HTTP_200_OK)


class BidsTendersListAPIView(APIView):
    """ Класс для получения списка предложений для тендера """

    # permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request: Request, tenderId: str) -> Response:
        user = request.query_params.get("username")
        limit = int(request.GET.get('limit', 5))
        offset = int(request.GET.get('offset', 0))
        try:
            tender = Tenders.objects.get(tenderId=tenderId)
            bids = Bids.objects.filter(tenderId=tenderId).order_by("bidName")[offset:offset + limit]
            if user == tender.creatorUsername:
                try:
                    serialized_tenders = []
                    for bid in bids:
                        serialized_tender = {
                            "id": bid.bidId,
                            "name": bid.bidName,
                            "status": bid.bidStatus,
                            "authorType": bid.bidAuthorType,
                            "authorId": bid.bidAuthorId.id,
                            "version": bid.bidVersion,
                            "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        }
                        serialized_tenders.append(serialized_tender)

                    return Response(status=HTTP_200_OK, data=serialized_tenders)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)
        except Tenders.DoesNotExist:
            return Response(data={"reason": "Тендер не найден"},
                            status=HTTP_404_NOT_FOUND)


class BidsStatusAPIView(APIView):
    """ Класс для получения и изменения статуса предложения """

    # permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request: Request, bidId: str) -> Response:
        user = request.query_params.get("username")
        try:
            bid = Bids.objects.get(bidId=bidId)
            if user == bid.authorId.username:
                requUser = Employee.objects.get(username=user)
                reqOrganization = OrganizationResponsible.objects.get(user_id=requUser)
                if bid.organizationId != reqOrganization.organization_id:
                    return Response(status=HTTP_403_FORBIDDEN,
                                    data={"reason": "Недостаточно прав для выполнения действия."})
                return Response(status=HTTP_200_OK, data=bid.bidStatus)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)

        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)

    def put(self, request: Request, bidId: str) -> Response:
        user = request.query_params.get("username")
        try:
            bid = Bids.objects.get(bidId=bidId)
            if user == bid.bidAuthorId.username:
                requUser = Employee.objects.get(username=user)
                reqOrganization = OrganizationResponsible.objects.get(user_id=requUser)
                if bid.organizationId != reqOrganization.organization_id:
                    return Response(status=HTTP_403_FORBIDDEN,
                                    data={"reason": "Недостаточно прав для выполнения действия."})
                try:
                    status = request.query_params.get("status")
                    bid.bidVersion += 1
                    bid.bidStatus = status
                    bid.save()

                    response_data = {
                        "id": bid.bidId,
                        "name": bid.bidName,
                        "status": bid.bidStatus,
                        "authorType": bid.bidAuthorType,
                        "authorId": bid.bidAuthorId.id,
                        "version": bid.bidVersion,
                        "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)


class BidsEditAPIView(APIView):
    """ Класс для редактирования параметров предложения """

    # permission_classes = [permissions.IsAuthenticated, ]

    def patch(self, request: Request, bidId: str) -> Response:
        user = request.query_params.get("username")
        try:
            bid = Bids.objects.get(bidId=bidId)
            if user == bid.bidAuthorId.username:
                requUser = Employee.objects.get(username=user)
                reqOrganization = OrganizationResponsible.objects.get(user_id=requUser)
                if bid.organizationId != reqOrganization.organization_id:
                    return Response(status=HTTP_403_FORBIDDEN,
                                    data={"reason": "Недостаточно прав для выполнения действия."})
                try:
                    if "name" in request.data:
                        bid.bidName = request.data.get("name")
                    if "description" in request.data:
                        bid.bidDescription = request.data.get("description")

                    bid.bidVersion += 1
                    bid.save()

                    response_data = {
                        "id": bid.bidId,
                        "name": bid.bidName,
                        "status": bid.bidStatus,
                        "authorType": bid.bidAuthorType,
                        "authorId": bid.bidAuthorId.id,
                        "version": bid.bidVersion,
                        "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)


class BidsDecisionAPIView(APIView):
    """ Класс для отправки решения по предложению """

    # permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request: Request, bidId: str) -> Response:
        user = request.query_params.get("username")
        decision = request.query_params.get("decision")
        try:
            bid = Bids.objects.get(bidId=bidId)
            if user == bid.bidAuthorId.username:
                requUser = Employee.objects.get(username=user)
                reqOrganization = OrganizationResponsible.objects.get(user_id=requUser)
                if bid.organizationId != reqOrganization.organization_id:
                    return Response(status=HTTP_403_FORBIDDEN,
                                    data={"reason": "Недостаточно прав для выполнения действия."})
                try:
                    if decision in ["Approved", "Rejected"]:
                        bid.bidDecision = decision
                        bid.bidVersion += 1
                        if decision == "Rejected":
                            bid.bidStatus = "Canceled"
                    else:
                        return Response(status=HTTP_400_BAD_REQUEST, data="Решение не может быть отправлено")

                    response_data = {
                        "id": bid.bidId,
                        "name": bid.bidName,
                        "status": bid.bidStatus,
                        "authorType": bid.bidAuthorType,
                        "authorId": bid.bidAuthorId.id,
                        "version": bid.bidVersion,
                        "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }
                    bid.save()
                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)


class BidsFeedbackAPIView(APIView):
    """ Класс для отправки отзыва по предложению """

    # permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request: Request, bidId: str):
        user = request.query_params.get("username")
        try:
            bid = Bids.objects.get(bidId=bidId)
            if user == bid.bidAuthorId.username:
                requUser = Employee.objects.get(username=user)
                reqOrganization = OrganizationResponsible.objects.get(user_id=requUser)
                if bid.organizationId != reqOrganization.organization_id:
                    return Response(status=HTTP_403_FORBIDDEN,
                                    data={"reason": "Недостаточно прав для выполнения действия."})
                try:
                    review = Reviews.objects.create(
                        bidReviewDescription=request.query_params.get("bidFeedback"),
                        bidFeedback=bid
                    )
                    bid.version += 1

                    response_data = {
                        "id": bid.bidId,
                        "name": bid.bidName,
                        "status": bid.bidStatus,
                        "authorType": bid.bidAuthorType,
                        "authorId": bid.bidAuthorId.id,
                        "version": bid.bidVersion,
                        "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)


class BidsRollbackAPIView(APIView):
    """ Класс для отката версии предложения """

    # permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request: Request, bidId: str, version: int) -> Response:
        user = request.query_params.get("username")
        try:
            bid = Bids.objects.get(bidId=bidId)
            if user == bid.bidAuthorId.username:
                reqUser = Employee.objects.get(username=user)
                reqOrganization = OrganizationResponsible.objects.get(user_id=reqUser)
                if bid.organizationId != reqOrganization.organization_id:
                    return Response(status=HTTP_403_FORBIDDEN,
                                    data={"reason": "Недостаточно прав для выполнения действия"})

                try:
                    bid.bidVersion = version
                    bid.save()
                    response_data = {
                        "id": bid.bidId,
                        "name": bid.bidName,
                        "status": bid.bidStatus,
                        "authorType": bid.bidAuthorType,
                        "authorId": bid.bidAuthorId.id,
                        "version": bid.bidVersion,
                        "createdAt": bid.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    return Response(status=HTTP_200_OK, data=response_data)
                except Exception as e:
                    return Response({"reason": f"{str(e)} Неверный формат запроса или его параметры."},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"reason": "Пользователь не существует или некорректен."},
                                status=HTTP_401_UNAUTHORIZED)
        except Bids.DoesNotExist:
            return Response(data={"reason": "Предложение не найдено"},
                            status=HTTP_404_NOT_FOUND)


class BidsReviewsAPIView(APIView):
    """ Класс для просмотра отзывов на прошлые предложения """

    # permission_classes = [permissions.IsAuthenticated, ]
    def get(self, request: Request, tenderId: str) -> Response:
        authorUsername = request.query_params.get("authorUsername")
        requesterUsername = request.query_params.get("requesterUsername")
        limit = int(request.GET.get('limit', 5))
        offset = int(request.GET.get('offset', 0))

        try:
            bids = Bids.objects.get(tenderId=tenderId)
        except Bids.DoesNotExist:
            return Response({"reason": "Тендер не найден"}, status=HTTP_404_NOT_FOUND)

        requUser = Employee.objects.get(username=requesterUsername)
        reqOrganization = OrganizationResponsible.objects.get(user_id=requUser)
        if bids.organizationId != reqOrganization.organization_id:
            return Response(status=HTTP_403_FORBIDDEN, data={"reason": "Недостаточно прав для выполнения действия."})

        if authorUsername is None or requesterUsername is None:
            return Response({"reason": "Неверный формат запроса или его параметры"}, status=HTTP_400_BAD_REQUEST)

        if authorUsername != bids.bidAuthorId.username:
            return Response({"reason": "Пользователь не существует или некорректен"}, status=HTTP_401_UNAUTHORIZED)

        reviews = Reviews.objects.filter(bidFeedback=bids.bidId)[offset:offset + limit]
        if not reviews:
            return Response({"reason": "Отзывы не найдены"}, status=HTTP_404_NOT_FOUND)

        serialized_reviews = []
        for review in reviews:
            serialized_review = {
                "id": review.bidReviewId,
                "description": review.bidReviewDescription,
                "createdAt": review.createdAt.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            serialized_reviews.append(serialized_review)

        return Response(data=serialized_reviews, status=HTTP_200_OK)

