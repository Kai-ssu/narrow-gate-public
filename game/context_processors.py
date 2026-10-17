from django.conf import settings


def site(request):
    """Site-wide names and links, available in every template."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "PUBLIC_REPO_URL": settings.PUBLIC_REPO_URL,
        "AUTHOR_URL": settings.AUTHOR_URL,
    }
