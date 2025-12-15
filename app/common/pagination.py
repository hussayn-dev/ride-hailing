from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE = 1


class CustomPagination(PageNumberPagination):
    # page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": int(self.request.GET.get("page", DEFAULT_PAGE)),
                "page_size": int(self.request.GET.get("page_size", self.page_size)),
                "results": data,
            }
        )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class LargeDatasetKeySetPagination(CursorPagination):
    ordering = "-created_at"  # Field used for pagination (should be indexed)
    page_size = 10  # Number of records per page
    max_page_size = 50
    page_size_query_param = "page_size"
