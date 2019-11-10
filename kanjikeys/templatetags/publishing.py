
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter
from django import template
register = template.Library()

# Leker lite med att modda template-motorn.

@register.filter
def longerthan(value, arg):
    return len(value) > int(arg)


@register.filter(name='linebreaksp')
def linebreaksp(value, autoescape=None):
    """
    Converts all newlines in a piece of plain text to HTML p tags, ending
	and beginning.
    """
    if autoescape and not isinstance(value, SafeData):
        from django.utils.html import escape
        value = escape(value)
    return mark_safe(value.replace(
		'\r\n\r\n', '\n\n'
	).replace(
		'\n\n', '&nbsp;</p><p>&nbsp;</p><p class="first">'
	).replace(
		'\n', '&nbsp;</p><p>')
	)
linebreaksp.is_safe = True
linebreaksp.needs_autoescape = True
linebreaksp = stringfilter(linebreaksp)

