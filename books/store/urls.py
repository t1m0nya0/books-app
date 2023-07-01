from django.urls import path, include
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, UserBookRelationView

router = SimpleRouter()

router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)

urlpatterns = [

]

urlpatterns += router.urls
