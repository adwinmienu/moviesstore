from django import template

register = template.Library()

@register.filter
def poster_url_or_default(poster, default_path='/static/img/placeholder-film.png'):
    if poster and hasattr(poster, 'url') and poster.url:
        return poster.url
    return default_path