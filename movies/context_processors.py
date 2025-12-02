from .models import Movie
import random


def featured_movie(request):
    """Context processor that returns a featured movie (random latest fallback).

    Returns a dict with key `featured_movie` set to a Movie instance or None.
    """
    try:
        # Prefer a random movie if any exist
        qs = Movie.objects.all()
        count = qs.count()
        if count == 0:
            return {'featured_movie': None}
        # choose a random item for simple "featured" behavior
        idx = random.randint(0, count - 1)
        movie = qs[idx]
        return {'featured_movie': movie}
    except Exception:
        # In case migrations haven't been run or DB isn't available, fail safely
        return {'featured_movie': None}
