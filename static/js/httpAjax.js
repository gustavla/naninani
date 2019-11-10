var httpAjax = false; 

function ajaxExec(url, ready_callback)
{
	httpAjax = false; 
    handler = false; 
    if (window.XMLHttpRequest) { 
        httpAjax = new XMLHttpRequest(); 
        if (httpAjax.overrideMimeType) { 
            httpAjax.overrideMimeType('text/xml'); 
        } 
    } else if (window.ActiveXObject) { 
        try { 
            httpAjax = new ActiveXObject("Msxml2.XMLHTTP"); 
        } catch (e) { 
            try { 
                httpAjax = new ActiveXObject("Microsoft.XMLHTTP"); 
            } catch (e) { 
                alert("Couldn´t build an AJAX instance."); 
                return false; 
            } 
        } 
    } 
    try { 
        httpAjax.onreadystatechange = ready_callback; 
    } catch (e) { 
        alert("onreadystatechange didn´t go well!"); 
        return false; 
    } 
    try { 
		httpAjax.open('GET', url, true); 
    } catch (e) { 
        alert("Couldn´t open url."); 
        return false; 
    }
    try { 
        httpAjax.send(null); 
    } catch (e) { 
        alert("Couldn´t send request."); 
        return false; 
    }
    return true;
}

function ajaxOK()
{
	return (httpAjax && httpAjax.readyState == 4);
}

function ajaxContent()
{
	return httpAjax.responseText;
}

function ajaxXMLContent()
{
	return httpAjax.responseXML.documentElement;
}


