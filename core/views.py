import logging

from django.views.generic import TemplateView

from core.cache import cache
from core.constants import ONE_DAY, VEHICLE_TYPES_CACHE_KEY
from core.models import VehicleType


logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle_types = cache.get(VEHICLE_TYPES_CACHE_KEY)
        if not vehicle_types:
            logger.debug(f'Cache miss: {VEHICLE_TYPES_CACHE_KEY}')
            vehicle_types = VehicleType.objects.all()[:3]
            cache.set(VEHICLE_TYPES_CACHE_KEY, vehicle_types, ONE_DAY)
        context['vehicle_types'] = vehicle_types
        return context
