from django import template
from django.template.defaultfilters import stringfilter

import util
import mistune as md
from mistune import escape
from pygments import highlight
from pygments.lexers import get_lexer_by_name, _iter_lexerclasses
from pygments.formatters import HtmlFormatter
from pygments.modeline import get_filetype_from_buffer
from pygments.util import ClassNotFound

register = template.Library()

class CustomizedRenderer(md.HTMLRenderer):

    lt = {}
    scene_props = {}
    scene_cnt = 0

    def ascii_render(self, code):
        div_id = self.scene_cnt
        self.scene_cnt += 1
        props, rendered = util.ascii_render(code)
        self.scene_props[div_id] = props
        return f'<div class="asciirend" id="asciirend-{div_id}"><pre>{rendered}</pre></div>';

    def block_code(self, code, info=None):
        if info:
            if info == 'asciirend':
                return self.ascii_render(code)
            lexer = get_lexer_by_name(info, stripall=True)
        else:
            try:
                lexer = util.guess_lexer(code)
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

    def link(self, text, url, title = None):
        if url.startswith("#") and not url[1:] in self.lt:
            self.lt[text] = url[1:]
        return super(CustomizedRenderer, self).link(text, url, title)

class ShortdownRenderer(md.HTMLRenderer):

    def heading(self, text, level):
        return '%s' % (text)

    def link(self, text, url, title = None):
        return '%s' % escape(text, quote=True)

@register.filter()
@stringfilter
def shortdown(value):
    renderer = ShortdownRenderer()
    md_rend = md.create_markdown(renderer=renderer, plugins=['strikethrough'])
    return md_rend(util.trimdown(value))

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
            javascript += f'ascii_render("asciirend-{i}", scene_{i}, {props["w"] if not props["dynamic_w"] else "null"}, {props["h"] if not props["dynamic_h"] else "null"}, {"true" if props["ortho"] else "false"}, {props["fov"]}, {props["znear"]}, {props["zfar"]}, {"true" if props["show_usage"] else "false"}, {"true" if props["disable_zoom"] else "false"});\n'
        javascript += """
</script>
        """
    else:
        javascript = ''
    return rendered + javascript
