from django.db import connection
from django.http import JsonResponse


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            {
                "status": "healthy",
                "database": "connected",
            },
            status=200,
        )

    except Exception:
        return JsonResponse(
            {
                "status": "unhealthy",
                "database": "unavailable",
            },
            status=503,
        )