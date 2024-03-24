from django.http import QueryDict
import json


def clean_data(request):
    """
    Retrieves the request data irrespective of the method and type it was sent.
    @param request: The Django HttpRequest
    @type request: WSGIRequest
    @return: The data from the request as a dict
    @rtype: QueryDict
    """
    data = None
    if request is not None:
        request_meta = getattr(request, 'META', {})
        request_method = getattr(request, 'method', None)
        if request_meta.get('CONTENT_TYPE', '') == 'application/json':
            data = json.loads(request.body)
        elif str(request_meta.get('CONTENT_TYPE', '')).startswith('multipart/form-data;'):
            # Form Data?
            data = request.POST.copy()
            data = data.dict()
        elif request_method == 'GET':
            data = request.GET.copy()
            data = data.dict()
        elif request_method == '':
            data = request.POST.copy()
            data = data.dict()
        if not data:
            request_body = getattr(request, 'body', None)
            if request_body:
                data = json.loads(request_body)
            else:
                data = QueryDict()
        return data
