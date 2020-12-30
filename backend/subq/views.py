from rest_framework.viewsets import ModelViewSet
from subq.serializers import SubQSerializer, SubQFollowerSerializer
from subq.models import SubQ, SubQFollower


class SubQViewSet(ModelViewSet):
    queryset = SubQ.objects.order_by('pk')
    serializer_class = SubQSerializer


class SubQFollowerViewSet(ModelViewSet):
    queryset = SubQFollower.objects.order_by('pk')
    serializer_class = SubQFollowerSerializer
