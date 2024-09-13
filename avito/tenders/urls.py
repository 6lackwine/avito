from django.urls import path

from .views import TendersAPIView, PingAPIView, TendersNewAPIView, TendersStatusAPIView,\
    TendersEditAPIView, TendersRollbackVersionAPIView, UserTendersListAPIView, BidsNewAPIView,\
    BidsMyAPIView, BidsTendersListAPIView, BidsStatusAPIView, BidsEditAPIView, BidsDecisionAPIView, \
    BidsFeedbackAPIView, BidsRollbackAPIView, BidsReviewsAPIView

urlpatterns = [
    path("ping", PingAPIView.as_view(), name="ping"),
    path("tenders", TendersAPIView.as_view(), name="tenders"),
    path("tenders/new", TendersNewAPIView.as_view(), name="tenders_new"),
    path("tenders/<str:tenderId>/status", TendersStatusAPIView.as_view(), name="tenders_status"),
    path("tenders/<str:tenderId>/edit", TendersEditAPIView.as_view(), name="tenders_edit"),
    path("tenders/<str:tenderId>/rollback/<int:version>", TendersRollbackVersionAPIView.as_view(), name="tenders_rollback"),
    path("tenders/my", UserTendersListAPIView.as_view(), name="tenders_my"),

    path("bids/new", BidsNewAPIView.as_view(), name="bids_new"),
    path("bids/my", BidsMyAPIView.as_view(), name="bids_my"),
    path("bids/<str:tenderId>/list", BidsTendersListAPIView.as_view(), name="bids_list"),
    path("bids/<str:bidId>/status", BidsStatusAPIView.as_view(), name="bids_status"),
    path("bids/<str:bidId>/edit", BidsEditAPIView.as_view(), name="bids_edit"),
    path("bids/<str:bidId>/submit_decision", BidsDecisionAPIView.as_view(), name="bids_decision"),
    path("bids/<str:bidId>/feedback", BidsFeedbackAPIView.as_view(), name="bids_feedback"),
    path("bids/<str:bidId>/rollback/<int:version>", BidsRollbackAPIView.as_view(), name="bids_rollback"),
    path("bids/<str:tenderId>/reviews", BidsReviewsAPIView.as_view(), name="bids_reviews"),

]