from django.db import models
import datetime
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
import re


KANJI_TYPES = (
    ('kanji', _('Kanji')),
    ('primitive', _('Primitive')),
)

class Kanji(models.Model):
    lesson = models.IntegerField(verbose_name=_("lesson"))
    kanji_type = models.CharField(max_length=15, choices=KANJI_TYPES, verbose_name=_("kanji type"))
    heisig = models.IntegerField(null=True, blank=True, verbose_name=_("ID"))
    comment = models.TextField(blank=True, verbose_name=_("comment"))
    before_heisig = models.IntegerField(null=True, blank=True, verbose_name=_("before ID"))
    order = models.IntegerField(null=True, blank=True, verbose_name=_("ordering"))
    strokes = models.IntegerField(blank=False, null=False, verbose_name=_("strokes"))
    kanji = models.CharField(max_length=1, blank=True, verbose_name=_("character"))
    keyword_sv = models.CharField(max_length=63, verbose_name=_("meaning (Swedish)"))
    keyword_en = models.CharField(max_length=63, verbose_name=_("meaning (English)"))
    # add_keywords_sv = models.CharField(max_length=127)
    # add_keywords_en = models.CharField(max_length=127)
    story_sv = models.TextField(blank=True, verbose_name=_("story (Swedish)"))
    story_en = models.TextField(blank=True, verbose_name=_("story (English)"))
    kanjidic = models.CharField(null=True, blank=True, max_length=255, verbose_name=_("kanjidic definition"))
    flagged = models.BooleanField(null=False, blank=False, verbose_name=_("flagged"))
    published = models.BooleanField(null=False, blank=False, verbose_name=_("published"))
    parts = models.ManyToManyField("self", symmetrical = False, related_name="children", blank=True, verbose_name=_("parts"))

    class Meta:
        verbose_name = _('character')
        verbose_name_plural = _('characters')
        ordering = ('order',)

    def __str__(self):
        return "("+self.kanji_fancy()+") " + self.keyword_sv# (for debugging)  + " " + str(self.heisig)

    # Kanji fancy is just adding an asterisk if there's no kanji symbol
    def kanji_fancy(self):
        if self.kanji == '':
            return u"\uFF0A"
        else:
            return self.kanji

    def stroy_hash_ref(self, kanji_id):
        try:
            k = Kanji.objects.get(id=int(kanji_id))
        except:
            return "#" + str(kanji_id) + " (unresolved kanji reference)"
        else:
            return '<a href="#' + str(kanji_id) + '" onclick="load_kanjicard(' + str(kanji_id) + ')">' + k.kanji + "</a> (" + k.keyword_sv + ")"

    # Returns the Swedishs story with hash references resolved (like "Look at character #232 for more details")
    def story_fancy(self):
        hashfinder = re.compile(r'\#(\d+)');
        pos = 0
        story = self.story_sv
        #


        while True:
            res = hashfinder.search(story, pos)
            if res is None:
                break
            else:
                kanji_id = int(res.group(1))
                str = self.stroy_hash_ref(kanji_id)
                story = story[0:res.start()] + str + story[res.end():]

                pos = res.start() + len(str)

        return story


    # This returns the keyword_sv, and appends additional
    #  meanings if they exist (returns an array)
    def all_meanings(self):
#        ret = [self.keyword_sv]
        meanings = Meaning.objects.filter(kanji=self)
        ret = [self.keyword_sv]+[m.sv for m in meanings]
        return ret

    # Used for exporting to JS
    def as_dictionary(self):
        meanings = Meaning.objects.filter(kanji=self)
        meanings_sv = [m.sv for m in meanings]
        meanings_kanji_id = [m.kanji_id for m in meanings]

        parts = self.parts.all()
        dict_parts = [{
            'id': p.id,
            'kanji': p.kanji_fancy(),
            'meanings': p.all_meanings(),
        } for p in parts]
#        parts_id = [p.id for p in parts]
#        parts_kanji = [p.kanji for p in parts]
#        parts_meanings = [p.all_meanings() for p in parts]

        dict_kanji = {
            'id': self.id,
            'kanji': self.kanji_fancy(),
            'kanji_type': self.kanji_type,
            'lesson': self.lesson,
            'heisig': self.heisig,
            'story_sv': self.story_fancy(),
            'strokes': self.strokes,
            'keyword_sv': self.keyword_sv,
            'meanings': meanings_sv,
            'meanings_kanji_id': meanings_kanji_id,
            'parts': dict_parts,
            'published': self.published,
#            'parts_id': parts_id,
#            'parts_kanji': parts_kanji,
#            'parts_meanings': parts_meanings,
        }
        return dict_kanji


class Meaning(models.Model):
    sv = models.CharField(max_length=63)
    en = models.CharField(max_length=63)
    kanji = models.ForeignKey(Kanji, models.CASCADE)

    class Meta:
        verbose_name = _('meaning')
        verbose_name_plural = _('meanings')

class Stat(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    kanji = models.ForeignKey(Kanji, models.CASCADE)
    timestamp = models.DateTimeField(blank=True)
    success = models.BooleanField()
    def __str__(self):
        if(self.success):
            return u"Successful attempt at %s by %s [%s]" % (self.kanji.kanji,
            self.user.username, str(self.timestamp))
        else:
            return u"Failed attempt at %s by %s [%s]" % (self.kanji.kanji,
            self.user.username, str(self.timestamp))


class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)

    lesson_from = models.IntegerField(blank=True, verbose_name=_("from lesson"))
    lesson_to = models.IntegerField(blank=True, verbose_name=_("to lesson"))

    # Det är bara skapa en en-US och ändra, ha! :P
    stat_color = models.CharField(max_length=15, verbose_name=_("statistics colour"))

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        ordering = ('user__username',)

    def __str__(self):
        return str(self.user)

#==========For auto-Admin=============
class KanjiInline(admin.TabularInline):
    model = Kanji
    extra = 3

class MeaningInline(admin.TabularInline):
#    verbose_name = _('meanings as primitive')
    model = Meaning
    extra = 3

#class ChapterAdmin(admin.ModelAdmin):
#    fields = ['number']
#    ordering = ('number',)

class KanjiAdmin(admin.ModelAdmin):
    inlines = [MeaningInline]
    list_display = ('kanji','keyword_sv','heisig','lesson','kanji_type','published')
    list_display_links = ('keyword_sv',)
    list_filter = ('published','flagged','kanji_type','lesson',)
    search_fields = ['=kanji','keyword_sv','keyword_en','=heisig']
    ordering = ('order',)
    filter_horizontal = ('parts',)
    fieldsets = [
        (_('More info'),
            {'fields':
                ('kanji_type',
                ('heisig','lesson','strokes',),
                'kanjidic',
#                ('before_heisig','order',)
                ),
            'classes': ['collapse']
            }
        ),
        (_('Parts'),
            {'fields':
                (
#                (('kanji_type', 'published',),
#                ('heisig','lesson',),
                'parts',),
            'classes': ['collapse']
            }
        ),
        (_('General'),
            {'fields':
                (
#                (('kanji_type', 'published',),
#                ('heisig','lesson',),
                ('flagged','published',),
                ('kanji','comment',),
                ('keyword_sv', 'keyword_en'),
                'story_sv',
                'story_en',)
            }
        ),
#        ('Heisig ID value',     {'fields': ['heisig']}),
#        ('Heisig ID value 2',     {'fields': ['kanji']}),
    ]
    class Media:
        css = {
            "all": ("css/editing.css",)
        }
        js = ('js/editing.js','js/httpAjax.js',)

#admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Kanji, KanjiAdmin)
admin.site.register(UserProfile)
