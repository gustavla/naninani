# coding: utf-8
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from kanjikeys.models import Kanji, Meaning, Stat
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime
from phyve import ajax
import math

@login_required
def promenad(request, kanji_id):
    width = 800.0
    height = 600.0
    # Promenad is a test application where you can examine the
    #  relationships of kanjis, and then take a walk among them.
    if kanji_id is 0:
        return HttpResponse('Menu for Promenad')

    if kanji_id.isdigit():
        kanji_id = int(kanji_id)
        try:
            kanji_raw = Kanji.objects.get(id=kanji_id)
        except:
            return HttpResponse('Kanji not found')
    else:
        try:
            # kanji_id is here regarded as the actual kanji
            kanji_raw = Kanji.objects.get(kanji=kanji_id)
        except:
            return HttpResponse('Kanji not found')

    kanji = kanji_raw
    parts = kanji_raw.parts.all()
    children = kanji_raw.children.all()
    # kanji = {
    #     'id': kanji_raw.id,
    #     'kanji': kanji_raw.kanji_fancy(),
    #     'meaning': kanji_raw.keyword_sv,
    # }
    #
    # parts = [{
    #     'id': p.id,
    #     'kanji': p.kanji_fancy(),
    #     'meaning': p.keyword_sv,
    # } for p in kanji_raw.parts.all()]
    #
    # children = [{
    #     'id': p.id,
    #     'kanji': p.kanji_fancy(),
    #     'meaning': p.keyword_sv,
    # } for p in kanji_raw.children.all()]



    svgdata = \
    """
    <!-- ECMAScript to change the radius with each click -->
  <script type="text/ecmascript"> <![CDATA[
    function hover(evt, info)
    {
        var circle = evt.target;
        var text = document.getElementById('debug');
        circle.setAttribute("fill", "#a21725");
        text.textContent = info;
        text.setAttribute("x", circle.getAttribute("x"))
        text.setAttribute("y", circle.getAttribute("y"))
    }
    function unhover(evt)
    {
        var circle = evt.target;
        circle.setAttribute("fill", "black");
        var text = document.getElementById('debug');
        text.textContent = "";
    }
  ]]> </script>

    """

    def text(x, y, kanji, keyword, size=20, kanji_id=0):
        return '<a xlink:href="/promenad/%(id)d/" xlink:type="simple"><text onmouseover="hover(evt, \'%(info)s\')" onmouseout="unhover(evt)" x="%(x)f%%" y="%(y)f%%" dy="%(sizehalf)f" fill="black" align="center" font-size="%(size)f" text-anchor="middle">%(text)s</text></a>' \
            % {"id": kanji_id, "x": x, "y": y, "text": kanji, "size": size, "sizehalf": size/2.0, "info": keyword.replace('"', '&#34;').replace('\'', '&#39;') }

    def arrow(x1, y1, x2, y2, cutoff=5):
        ang = -math.atan2(x2-x1, y2-y1)

        _x1 = x1 - math.sin(ang)*cutoff
        _y1 = y1 + math.cos(ang)*cutoff
        _x2 = x2 + math.sin(ang)*cutoff
        _y2 = y2 - math.cos(ang)*cutoff

        try:
            length = float(request.GET['length'])
        except:
            length = 2.0

        ret = '<line x1="%(x1)f%%" y1="%(y1)f%%" x2="%(x2)f%%" y2="%(y2)f%%" cx1="10" style="stroke:rgb(9,99,99); stroke-width:2" />' \
            % {"x1": _x1, "y1": _y1, "x2": _x2, "y2": _y2}

        ret += '<line x1="%(x1)f%%" y1="%(y1)f%%" x2="%(x2)f%%" y2="%(y2)f%%" cx1="10" style="stroke:rgb(9,99,99); stroke-width:2" />' \
            % {"x1": _x2+length*math.sin(ang+10.0*math.pi/180.0), "y1": _y2-length*math.cos(ang+10.0*math.pi/180.0), "x2": _x2, "y2": _y2}
        ret += '<line x1="%(x1)f%%" y1="%(y1)f%%" x2="%(x2)f%%" y2="%(y2)f%%" cx1="10" style="stroke:rgb(9,99,99); stroke-width:2" />' \
            % {"x1": _x2+length*math.sin(ang-10.0*math.pi/180.0), "y1": _y2-length*math.cos(ang-10.0*math.pi/180.0), "x2": _x2, "y2": _y2}
        return ret


    def set_stuff(num):
        if num>15:
            bang = 10.0
            dist = 45
            size = 15
        elif num>4:
            bang = 30.0
            dist = 30
            size = 20
        else:
            bang = 60.0
            dist = 20
            size = 20
        return (bang, dist, size)



    i = 0

    (bufferang, dist, size) = set_stuff(len(children))

    if len(children) is 1:
        ang = math.pi/2
    else:
        ang = bufferang * math.pi/180

    for k in children:
        x = 50 + dist*math.sin(ang)
        y = 50 - dist*math.cos(ang)
        svgdata += arrow(50, 50, x, y)
        svgdata += text(x, y, k.kanji_fancy(), k.keyword_sv, size, k.id)
        if len(children)>1:
            ang += (180-bufferang*2)*math.pi/180/(len(children)-1)

    (bufferang, dist, size) = set_stuff(len(parts))

    if len(parts) is 1:
        ang = math.pi/2
    else:
        ang = bufferang * math.pi/180

    for k in parts:
        x = 50 - dist*math.sin(ang)
        y = 50 - dist*math.cos(ang)
        svgdata += arrow(x, y, 50, 50)
        svgdata += text(x, y, k.kanji_fancy(), k.keyword_sv, size, k.id)
        if len(parts)>1:
            ang += (180-bufferang*2)*math.pi/180/(len(parts)-1)

    svgdata += text(50,50,kanji.kanji_fancy(), kanji.keyword_sv, 20, kanji.id)

    svgdata += \
    """
    <text x="0" y="0" dy="-20" fill="black" align="left" font-size="20" text-anchor="middle" id="debug"></text>
    """

    return render_to_response('kanjikeys/promenad.html', locals(), content_type="application/xhtml+xml")
