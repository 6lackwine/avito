import uuid

from django.core.validators import MinValueValidator
from django.db import models


class Tenders(models.Model):
    """ Класс для создания модели тендера """
    TENDER_STATUS = [
        ("Created", "Создан"),
        ("Published", "Опубликован"),
        ("Closed", "Закрыт"),
    ]

    TENDER_SERVICE_TYPE = [
        ("Construction", "Строительство"),
        ("Delivery", "Доставка"),
        ("Manufacture", "Производство"),
    ]

    tenderId = models.CharField(primary_key=True, default=uuid.uuid4())
    tenderName = models.CharField(max_length=100)
    tenderDescription = models.TextField(max_length=500)
    tenderServiceType = models.CharField(max_length=30, choices=TENDER_SERVICE_TYPE)
    tenderStatus = models.CharField(max_length=30, choices=TENDER_STATUS)
    organizationId = models.CharField
    tenderVersion = models.PositiveIntegerField(default=1, validators=[MinValueValidator(limit_value=1)])
    creatorUsername = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class Employee(models.Model):
    """ Класс для создания модели работника """
    id = models.CharField(primary_key=True, default=uuid.uuid4())
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Bids(models.Model):
    """ Класс для создания модели предложений """
    BIDS_STATUS = [
        ("Created", "Создано"),
        ("Published", "Опубликовано"),
        ("Canceled", "Закрыто")
    ]

    BID_AUTHOR_TYPE = [
        ("Organization", "Организация"),
        ("User", "Пользователь")
    ]

    BID_DECISION = [
        ("Approved", "Одобрено"),
        ("Rejected", "Отклонено")
    ]

    bidId = models.CharField(primary_key=True, default=uuid.uuid4())
    bidName = models.CharField(max_length=100)
    bidDescription = models.TextField(max_length=500)
    bidStatus = models.CharField(max_length=30, choices=BIDS_STATUS)
    tenderId = models.ForeignKey(Tenders, on_delete=models.CASCADE)
    organizationId = models.ForeignKey("Organization", on_delete=models.CASCADE)
    bidAuthorType = models.CharField(max_length=30, choices=BID_AUTHOR_TYPE)
    bidAuthorId = models.ForeignKey(Employee, on_delete=models.CASCADE)
    bidVersion = models.PositiveIntegerField(default=1, validators=[MinValueValidator(limit_value=1)])
    bidDecision = models.CharField(max_length=30, choices=BID_DECISION)
    createdAt = models.DateTimeField(auto_now_add=True)


class Organization(models.Model):
    """ Класс для создания модели организации """
    ORGANIZATION_TYPE = [
        ('IE', ""),
        ('LLC', "Limited Liability Company"),
        ('JSC', "Joint-stock company ")
    ]

    id = models.CharField(primary_key=True, default=uuid.uuid4())
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=30, choices=ORGANIZATION_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrganizationResponsible(models.Model):
    """ Класс для создания модели ответственного за организацию """
    id = models.CharField(primary_key=True, default=uuid.uuid4())
    user_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Reviews(models.Model):
    """ Класс для создания модели отзывов """
    bidReviewId = models.CharField(primary_key=True, default=uuid.uuid4())
    bidReviewDescription = models.TextField(max_length=1000)
    createdAt = models.DateTimeField(auto_now_add=True)