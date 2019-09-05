from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict 

class LimitOffsetPaginationWithDefault(LimitOffsetPagination):
    """
    Functions in a similar way as LimitOffsetPagination but has a provision
    for when offset and limit are not provided in request
    """
    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)

        if self.limit is None and self.offset == 0:
            return list(queryset)
        elif self.limit is None and self.offset != 0:
            return None
        else:
            self.request = request
            if self.count > self.limit and self.template is not None:
                self.display_page_controls = True

            if self.count == 0 or self.offset > self.count:
                return []
            
            return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data): 
        if self.count > len(data):
            return Response(OrderedDict([
                ('count', self.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('results', data)
            ]))
        elif self.count == len(data):
            return Response(data)