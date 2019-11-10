"""Todo: 
Possibly: json arguments (again, use python-cjson to decode...)
Prevent XSS and JS Hijacking http://www.fortifysoftware.com/servlet/downloads/public/JavaScript_Hijacking.pdf
Better error handling
Caching the generated script to a statically included file
Possibly detach code from prototype.js
Should load all modules referenced from ajax setting in the project settings-file
"""
#import cjson
import json
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from inspect import getargspec

try:
    for m in settings.AJAX_MODULES:
        print(m)
        #TODO: include the files...
except:
    #print 'NO GLOBAL AJAX!'
    pass #nothin to load


_functions = {}

#decorator
def register(func):
    _functions[func.__name__] = func
    return func

#view that handles ajax requests
def response_view(request, function):
    parameters = request.GET
    try:
        func = _functions[function]#_functions[parameters['_function']]    
        args = {}
        for p in getargspec(func)[0]:
            args[p] = parameters[p]
        return HttpResponse(content_type="application/json", #maybe mimetype?
            content='/*-secure-\n' + json.dumps(func(**args)) + '\n*/') #protects against JS hijacking
    except KeyError:
        return HttpResponse("ERROR: No such function in ajax dict (%s)" % function)

def script_view(request):
    return HttpResponse(content_type="application/javascript", content=script())
    
def script():
    js_arr = ["""
_sync_data = null;
function __bridge_request__(function_name, args, __callback__){
    var asynchronous = !!__callback__;
    new Ajax.Request('%s'.replace('__function__', function_name),{
        method: 'GET',
        parameters: args,
        asynchronous: asynchronous,
        onSuccess: function(transport){
            var data = transport.responseText;
            var json = data.evalJSON(true);
            if(asynchronous)
                __callback__(json);
            else
                _sync_data = json;
        },
        onFailure: function(){
            alert("Connection error");
        }
    });
    if(!asynchronous){
        tmp = _sync_data;
        _sync_data = null;
        return tmp;
    }
}
ajax = new Object();
"""%reverse(viewname = 'ajax_query', kwargs={'function':'__function__'})]
    #for ns in _namespaces:
    #    js_arr.append("%s = new Object();"%ns);
    for name, func in _functions.items():
        args = getargspec(func)[0]
        parts = []
        dparts = []
        for a in args:
            parts.append(a)
            dparts.append('%s:%s'%(a, a))
        argstring = ', '.join(parts)
        dictstring = ', '.join(dparts)
        if len(argstring):
            comma = ', '
        else:
            comma = ''
        js = """
ajax.%s = function (%s%s__callback__){
    return __bridge_request__('%s', {%s}, __callback__);
}""" % (name, argstring, comma, name, dictstring)
        js_arr.append(js)

    return '\n'.join(js_arr)
