from django import template
from django.template.defaultfilters import stringfilter

import mistune as md
from mistune import escape
from pygments import highlight
from pygments.lexers import get_lexer_by_name, _iter_lexerclasses
from pygments.formatters import HtmlFormatter
from pygments.modeline import get_filetype_from_buffer
from pygments.util import ClassNotFound

import asciirend as ar
import tomllib

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

class CustomizedRenderer(md.HTMLRenderer):

    lt = {}
    scene_props = {}
    scene_cnt = 0

    def ascii_render(self, code):
        div_id = self.scene_cnt
        self.scene_cnt += 1
        d = code.split('{', 1)
        if len(d) == 1:
            scene = code
        else:
            props = tomllib.loads(d[0])
            scene = '{' + d[1]

        color = int(props['color']) if 'color' in props else 0
        w = int(props['w']) if 'w' in props else 64
        h = int(props['h']) if 'h' in props else 32
        aspect = float(w / (2 * h))
        ortho = bool(props['ortho']) if 'ortho' in props else True
        fov = float(props['fov']) if 'fov' in props else 1.0
        znear = float(props['znear']) if 'znear' in props else 0.1
        zfar = float(props['zfar']) if 'zfar' in props else 100.0

        self.scene_props[div_id] = {
            'scene': scene,
            'w': w,
            'h': h,
            'aspect': aspect,
            'ortho': ortho,
            'fov': fov,
            'znear': znear,
            'zfar': zfar,
            'dynamic_w': bool(props['dynamic_w']) if 'dynamic_w' in props else False,
            'dynamic_h': bool(props['dynamic_h']) if 'dynamic_h' in props else False,
        }

        rendered = ar.ascii_render(scene, color, w, h, aspect, ortho, fov, znear, zfar)
        return f'<div class="asciirend" id="asciirend-{div_id}"><pre>{rendered}</pre></div>';

    def block_code(self, code, lang=None):
        if lang:
            if lang == 'asciirend':
                return self.ascii_render(code)
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                lexer = get_lexer_by_name("html", stripall=True)

        print(str(lexer))

        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)

    def heading(self, text, level):
        if text in self.lt:
            return '<h%d id="%s">%s</h%d>\n' % (level, self.lt[text], text, level) 
        else:
            return super(CustomizedRenderer, self).heading(text, level)

    def link(self, link, text, title):
        if link.startswith("#") and not link[1:] in self.lt:
            self.lt[text] = link[1:]
        return super(CustomizedRenderer, self).link(link, text, title)

class ShortdownRenderer(md.HTMLRenderer):

    def heading(self, text, level):
        return '%s' % (text)

    def link(self, link, text, title):
        return '%s' % escape(text, quote=True)


@register.filter()
@stringfilter
def shortdown(value):
    max_len = 500
    lbtrim_len = 100
    mstr = (value[:(max_len - 3)].strip() + "...") if len(value) > max_len else value
    left = mstr[:lbtrim_len]
    right = mstr[lbtrim_len:]

    right_split = right.splitlines()

    trimmed = (left + right_split[0]) if len(right_split) > 0 else left

    renderer = ShortdownRenderer()
    md_rend = md.create_markdown(renderer=renderer, plugins=['strikethrough'])
    return md_rend(trimmed)

@register.filter()
@stringfilter
def markdown(value):
    renderer = CustomizedRenderer()
    md_rend = md.create_markdown(renderer=renderer, plugins=['task_lists', 'table', 'footnotes', 'strikethrough'])
    rendered = md_rend(value)
    if renderer.scene_cnt > 0:
        javascript = """
<script type="module">
	import ascii_render from "/static/js/draw.js";
        """
        for i in range(renderer.scene_cnt):
            props = renderer.scene_props[i]
            javascript += f'const scene_{i} = \'{props["scene"].rstrip()}\';\n'
            javascript += f'ascii_render("asciirend-{i}", scene_{i}, {props["w"] if not props["dynamic_w"] else "null"}, {props["h"] if not props["dynamic_h"] else "null"}, {"true" if props["ortho"] else "false"}, {props["fov"]}, {props["znear"]}, {props["zfar"]});\n'
        javascript += """
</script>
        """
    else:
        javascript = ''
    return rendered + javascript
