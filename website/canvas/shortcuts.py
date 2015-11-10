from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from canvas.templatetags.jinja_base import render_jinja_to_string

def r2r(template, locals_vars, extra_context={}):
    return render_to_response(template, locals_vars,
                              context_instance=RequestContext(locals_vars['request'], extra_context))

def r2r_jinja(template, context, request=None, **response_kwargs):
    if request:
        context = RequestContext(request, context)
    response_kwargs.setdefault('content_type', 'text/html')
    response_kwargs.setdefault('status', 200)
    return HttpResponse(render_jinja_to_string(template, context), **response_kwargs)

def direct_to_template(request, template, **kwargs):
    """ Uses jinja. """
    return r2r_jinja('%s' % template, dict(kwargs), request=request)

