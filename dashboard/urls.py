from django.conf.urls import patterns, url

from dashboard.views import OrdersDashboard, AcceptOrder, CancelOrder, CompleteOrder, Poll


urlpatterns = patterns(
    '',
    url(r'^$', OrdersDashboard.as_view(), name="home"),
    url(r'^accept-order/$', AcceptOrder.as_view(), name="accept-order"),
    url(r'^cancel-order/cancel/$', CancelOrder.as_view(), {'cancel_verb': 'canceled'}, name="cancel-order-cancel"),
    url(r'^cancel-order/decline/$', CancelOrder.as_view(), {'cancel_verb': 'declined'}, name="cancel-order-decline"),
    url(r'^complete-order/$', CompleteOrder.as_view(), name="complete-order"),
    url(r'^poll/$', Poll.as_view(), name="poll"),
)
