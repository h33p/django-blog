from django import template
from django.template.defaultfilters import stringfilter

import mistune as md
from pygments import highlight
from pygments.lexers import get_lexer_by_name, _iter_lexerclasses
from pygments.formatters import HtmlFormatter
from pygments.modeline import get_filetype_from_buffer
from pygments.util import ClassNotFound

register = template.Library()

def guess_lexer(_text, conf_threshold = 0.01, mime_mul = 0.09, **options):
    """Guess a lexer by strong distinctions in the text (eg, shebang)."""

    # try to get a vim modeline first
    ft = get_filetype_from_buffer(_text)

    if ft is not None:
        try:
            return get_lexer_by_name(ft, **options)
        except ClassNotFound:
            pass

    best_lexer = [0.0, None]
    for lexer in _iter_lexerclasses():
        rv = lexer.analyse_text(_text)

        #MIME has an unusually high rv when providing it with any kind of text
        if 'MIME' in str(lexer):
            rv *= mime_mul

        if rv == 1.0:
            return lexer(**options)
        if rv > best_lexer[0]:
            best_lexer[:] = (rv, lexer)
    if not best_lexer[0] or best_lexer[0] < conf_threshold or best_lexer[1] is None:
        raise ClassNotFound('no lexer matching the text found')
    return best_lexer[1](**options)

class CustomizedRenderer(md.Renderer):

    lt = {}

    def block_code(self, code, lang):
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                lexer = get_lexer_by_name("html", stripall=True)

        print(str(lexer))

        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)

    def header(self, text, level, raw=None):
        if text in self.lt:
            return '<h%d id="%s">%s</h%d>\n' % (level, self.lt[text], text, level) 
        else:
            return super(CustomizedRenderer, self).header(text, level, raw=raw)

    def link(self, link, title, text):
        if link.startswith("#") and not link[1:] in self.lt:
            self.lt[text] = link[1:]
        return super(CustomizedRenderer, self).link(link, title, text)

class ShortdownRenderer(md.Renderer):

    def link(self, link, title, text):
        return '<a title="%s">%s</a>' % (title, text)


@register.filter()
@stringfilter
def shortdown(value):
    max_len = 500
    lbtrim_len = 100
    mstr = (value[:(max_len - 3)] + "...") if len(value) > max_len else value
    left = mstr[:lbtrim_len]
    right = mstr[lbtrim_len:]

    right_lines = right.splitlines()

    trimmed = left + (right_lines[0]) if len(right_lines) > 0 else ""

    renderer = ShortdownRenderer()
    md_rend = md.Markdown(renderer=renderer, plugins=[''])
    return md_rend(trimmed)

@register.filter()
@stringfilter
def markdown(value):
    renderer = CustomizedRenderer()
    md_rend = md.Markdown(renderer=renderer)
    return md_rend(value)
