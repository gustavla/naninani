from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

@login_required
def kanji(request):
    user_id = request.user.id
    user = request.user
    return render_to_response('kanjikeys/kanji.html', locals())

# Create your views here.
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from .models import Kanji, Meaning, Stat, UserProfile
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime
from phyve import ajax

def kanjicard_prepare(kanji_id):
    try:
        kanji_raw = Kanji.objects.get(id=kanji_id)
        kanji = kanji_raw.as_dictionary()
    except:
        return "Kanji not found"

    # This is hopefully temporary, because it's not very elegant and fast
    kanji_id_next = fetch_relative_to_id(kanji_id, 1)
    kanji_id_prev = fetch_relative_to_id(kanji_id, -1)
    return (kanji, kanji_id_next, kanji_id_prev,);

@ajax.register
def kanjicard(kanji_id):
    (kanji, kanji_id_next, kanji_id_prev) = kanjicard_prepare(kanji_id)
    return render_to_string('kanjikeys/kanjicard.html', locals())

@ajax.register
def kanjicard_lesson(kanji_id):
    (kanji, kanji_id_next, kanji_id_prev) = kanjicard_prepare(kanji_id)

    # Now let's get the lesson listing
    lesson_kanji_raw = Kanji.objects.filter(lesson=kanji['lesson']).order_by('order')
    lesson_kanji = [{
        'id': k.id,
        'kanji': k.kanji_fancy(),
        'kanji_type': k.kanji_type,
    } for k in lesson_kanji_raw]
    return render_to_string('kanjikeys/kanjicard_lesson.html', locals())

#@login_required
def complete_lesson(request, lesson_id):
    lesson_kanji_raw = Kanji.objects.filter(lesson=lesson_id).order_by('order')
    lesson_kanji = [kanjicard_prepare(k.id) for k in lesson_kanji_raw]
    kanjicards = [render_to_string('kanjikeys/kanjicard_pdf.html', {"kanji": kanji[0]}) for kanji in lesson_kanji]
#    for lesson_kanji in kanji
    no_backlink = True
    return render_to_response('kanjikeys/complete_lesson.html', locals())

@login_required
def lesson(request):
    user_id = request.user.id
    user = request.user
    return render_to_response('kanjikeys/lesson.html', locals())

@login_required
def lesson_list(request):
    user_id = request.user.id
    user = request.user
    # Det här är så fult och långsamt att jag mår illa.
    # Men tills kunskapen om Django är större...
    lessons = []
    for i in range(1,57):
        k = Kanji.objects.filter(lesson=i).order_by('order')[0]
        lessons.append({
            'lesson': k.lesson,
            'id': k.id,
            'break': (i%10 is 0),
        })
    return render_to_response('kanjikeys/lesson_list.html', locals())

@ajax.register
def fetch_random_kanjis(user_id):
    user = User.objects.get(id=user_id)
    try:
        user_profile = UserProfile.objects.get(user=user)
        lesson_from = user_profile.lesson_from
        lesson_to = user_profile.lesson_to
    except UserProfile.DoesNotExist:
        lesson_from = 0
        lesson_to = 0

    kanji_query = Kanji.objects.filter(
        kanji_type='kanji',
        published=1,
    ).order_by('?')

    if lesson_from and lesson_to:
        kanji_query = kanji_query.filter(
            lesson__gte=lesson_from,
            lesson__lte=lesson_to
        )

    bank_i = 0
    kanjis_raw = kanji_query[0:5]
    for k in kanjis_raw:
        i = 0
        while i<5:
            stat = Stat.objects.filter(user=user, kanji=k).order_by('-timestamp').values('success')[0:3]
            if len(stat) < 3: #This user needs to be tested more on this
                point = 0
            else:
                point = stat[0]['success'] + stat[1]['success'] + stat[2]['success']

            if point >= 2:
                try:
                    k = kanji_query[0]
                except:
                    break
            else:
                break

            i+= 1

    kanjis = []
    for kanji in kanjis_raw:
        kanjis.append( kanji.as_dictionary() )
    return kanjis

# This fetches relative to a kanji_id, it uses "order" as sorting,
#  so you can step through the kanji/primitives in the book's order.
def fetch_relative_to_id(kanji_id, rel):
    try:
        origo_kanji = Kanji.objects.get(id=kanji_id)

        # This looks intricate, the excludes() are for stepping through
        #  primitives with the same order value.
        if int(rel) >= 0:
            kanji = Kanji.objects.filter(
                order__gte=origo_kanji.order
            ).exclude(
                id__lte=origo_kanji.id,
                order=origo_kanji.order
            ).order_by('order', 'id')[int(rel)-1]
        else:
            kanji = Kanji.objects.filter(
                order__lte=origo_kanji.order
            ).exclude(
                id__gte=origo_kanji.id,
                order=origo_kanji.order
            ).order_by('-order', '-id')[0-int(rel)-1]
    except:
        return 0
    else:
        # It's expecting an array, since you can return several kanjis.
        return kanji.id

@ajax.register
def fetch_kanji(kanji_id):
    try:
        if int(kanji_id) == -1:
            kanji1 = Kanji.objects.filter(kanji_type='kanji', published=1).order_by('?')[0]
        else:
            kanji1 = Kanji.objects.get(id=kanji_id)
    except:
        return []
    else:
        # It's expecting an array, since you can return several kanjis.
        return [ kanji1.as_dictionary() ]

# Doesn't require login, which isn't good at all. Should ideally
#  take a request with a user object.
@ajax.register
def report_stat(user_id, kanji_id, success):
    stat = Stat(
        user_id=int(user_id),
        kanji_id=int(kanji_id),
        success=int(success),
        timestamp=datetime.now()
    )
    stat.save()
    return []

@ajax.register
def resave_story(user_id, kanji_id, story):
    try:
        kanji = Kanji.objects.get(id=kanji_id)
        kanji.story_sv = story
        kanji.save()
    except:
        pass
    return []

def translate(request):
    string = ''
    rest = ''
    try:
        string = request.GET['word']
        if len(string) > 25:
            rest = string[:-25]
            string = string[-25:]

        broken = string.split()
    except:
        return HttpResponse('')

    split_pos = 1
    count = len(broken)
    for i in range(0,count):
        word = " ".join(broken[i:])
        try:
            k = Kanji.objects.filter(keyword_en=word)[0]
            translation = k.keyword_sv
        except:
            pass
        else:
            return HttpResponse(rest+string[:-len(word)]+translation)

        try:
            k = Meaning.objects.filter(en=word)[0]
            translation = k.sv
        except:
            pass
        else:
            return HttpResponse(rest+string[:-len(word)]+translation)

    return HttpResponse('')

def login(request):
    return render_to_response('kanjikeys/login.html', locals())

def stats(request):
    from django.contrib.auth.models import User
    width = 800.0
    height = 600.0
    def diff_to_sec(timediff):
        return timediff.days*86400 + timediff.seconds

    graphs = {}
    all_stats = Stat.objects.order_by('timestamp')
    min_time = all_stats[0].timestamp
    max_time = datetime.now()#all_stats[all_stats.count()-1].timestamp
    time_norm = diff_to_sec(max_time - min_time)

    number_of_kanji = Kanji.objects.filter(kanji_type='kanji').count()

    for user in User.objects.all():
        points_for_kanji = {}
        stats = all_stats.filter(user=user).values()
        if(stats.count() < 1):#user should at least try...
            continue

        plot = [(0, height)]
        tot = 0.0
        for s in stats:
            oldval = points_for_kanji.get(s['kanji_id'], 0.0)
            if(s['success']):
                newval = min(1.0,  oldval + 1.0/3)
            else:
                newval = 0.0
            points_for_kanji[s['kanji_id']] = newval;
            tot += newval - oldval

            normed_time = float(diff_to_sec(s['timestamp']-min_time))/time_norm
            plot.append( (width*normed_time, height*(1-tot/number_of_kanji)) )

        plot.append((width+1, plot[len(plot)-1][1]))
        plot.append((width+1, height))

        try:
            color = user.get_profile().stat_color
        except:
            color = '#55f'

        graphs[user.username] = {'d': "M " + " L ".join(map(lambda x: "%.1f %.1f"%x, plot)),
                                'color': color,
                                'final_score': tot}

    num_pub_kanji = Kanji.objects.filter(kanji_type='kanji', published=True).count()
    limit_line_y = height*(1-float(num_pub_kanji)/number_of_kanji)
    return render_to_response('kanjikeys/stats.html', locals(), content_type="application/xhtml+xml")


# An alternative way of displaying statistics
def stats_overview(request, username):
    from django.contrib.auth.models import User
    width = 800.0
    height = 600.0

    all_stats = Stat.objects.order_by('timestamp')

    markup = {}
    for kanji in Kanji.objects.filter(kanji_type="kanji", published=True):
        markup[kanji.id] = 0

    user = User.objects.get(username=username)

#    for user in User.objects.all():
    points_for_kanji = markup
    stats = all_stats.filter(user=user).values()
#    if(stats.count() < 1):#user should at least try...
#        continue

    boxes = []

    plot = [(0, height)]
    tot = 0.0
    for s in stats:
        oldval = points_for_kanji.get(s['kanji_id'], 0.0)
        if(s['success']):
            newval = min(3,  oldval + 1)
        else:
            newval = 0
        points_for_kanji[s['kanji_id']] = newval;
        tot += newval - oldval

#            normed_time = float(diff_to_sec(s['timestamp']-min_time))/time_norm
#            plot.append( (width*normed_time, height*(1-tot/number_of_kanji)) )

#        plot.append((width+1, plot[len(plot)-1][1]))
#        plot.append((width+1, height))


    # 51 x 40

    levels = 0
    #perrow = 51
    def make_box(id, color):
        perrow = 50.0
        maxheight= 20
        dy = 600.0/(41.0)
        dx = 800.0/perrow
        startx = 0
        starty = 0
        size_x = dx
        size_y = dy

        y = 0
        x = (id-1)*dx
#        new_levels = 1
        while x >= dx*perrow:
            x -= dx*perrow
            y += dy
            #new_levels += 1

        return {
            "id": id,
            "x": startx + x,
            "y": starty + y,
            "width": size_x,
            "height": size_y,
            "color": color,
        }

    for k, v in points_for_kanji.items():
        if v is 0:
            boxes.append(make_box(k, "white"))
        else:
            color = 'red'
            if v is 1: color = '#c4df9b'
            if v is 2: color = '#6fc05d'
            if v is 3: color = '#428b38'
            boxes.append(make_box(k, color))

#    maxkanji = Kanji.objects.filter(kanji_type="kanji").count()
    maxkanji = 2042 # this won't change, might as well save us an sql query

    # Fill up the excess of the rectangle
    for i in range(maxkanji+1, 2050+1):
        boxes.append(make_box(i, "black"))

    texts = []
    for i in range(0,levels):
        texts.append({
            "x": startx + dx*perrow + 10,
            "y": starty + dy*i,
            "text": str(i*perrow + 1) + " - " + str(min(maxkanji, (i+1)*perrow)),
            "line_y": starty + dy*i + 2+(dy-maxheight)/2,
        })

    #num_pub_kanji = Kanji.objects.filter(kanji_type='kanji', published=True).count()
#    " L ".join(map(lambda x: "%.1f %.1f"%x, plot)),
#    "jsk[%d]='%s'"

    kanjis = Kanji.objects.filter(kanji_type='kanji', published=True).values('id', 'kanji', 'keyword_sv');

    jskanjis = "var jsk = new Array();var jsm = new Array();" + "".join(map(lambda x: "jsk[%(id)d]='%(k)s';jsm[%(id)d]='%(m)s';"%\
        {"id": x['id'], "k": x['kanji'], "m": x['keyword_sv']}, kanjis))

    data = {'boxes': boxes, 'width': width, 'height': height, 'jskanjis': jskanjis}
    return render_to_response('kanjikeys/stats_overview.html', data, content_type="application/xhtml+xml")


# Jag leker bara lite med cirkeldiagram
from svgee.models import Piechart
def stats_pie(request):
    chart = Piechart()
    import random
#    chart.parts = [[34, 'blue'], [104, 'red'], [232, 'yellow'], [12, 'green'], [40, 'purple'], [56, 'brown']]
    chart.side = 240
    chart.r = 100
    chart.add_part(value=2062761, color="#FF0000", text="Socialdemokraterna")
    chart.add_part(value=1199394, color="blue", text="Moderata samlingspartiet")
    chart.add_part(value=499356, color="#3399FF", text="Folkpartiet liberalerna")
    chart.add_part(value=465175, color="#009933", text="Centerpartiet")
    chart.add_part(value=390351, color="#003399", text="Kristdemokraterna", pulled_out=20)
    chart.add_part(value=368281, color="gold", text="Ny demokrati")
    chart.add_part(value=246905, color="#A11C21", text="Vänsterpartiet")
    chart.add_part(value=185051, color="#61BF1A", text="Miljöpartiet")
    chart.add_part(value=53487, color="gray", text="Övriga partier")
    (svgpie, svgpie_js, pielegend) = chart.svg_and_js()

    chart2 = Piechart()
    chart2.side = 60
    chart2.add_part(value=34, color="blue")
    chart2.add_part(value=104, color="red")
    chart2.add_part(value=232, color="gold")
    (svgpie2, svgpie_js2, pielegend2) = chart2.svg_and_js()

    return render_to_response('kanjikeys/stats_pie.html', locals(), content_type="application/xhtml+xml")

