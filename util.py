from pygments.modeline import get_filetype_from_buffer
from pygments.lexers import get_lexer_by_name, _iter_lexerclasses

import asciirend as ar
import tomllib

def trimdown(value):
    max_len = 500
    lbtrim_len = 100
    mstr = (value[:(max_len - 3)].strip() + "...") if len(value) > max_len else value
    left = mstr[:lbtrim_len]
    right = mstr[lbtrim_len:]

    right_split = right.splitlines()

    return (left + right_split[0]) if len(right_split) > 0 else left

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

def ascii_render(code):
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

    params = {
        'scene': scene.replace('\n', ''),
        'w': w,
        'h': h,
        'aspect': aspect,
        'ortho': ortho,
        'fov': fov,
        'znear': znear,
        'zfar': zfar,
        'dynamic_w': bool(props['dynamic_w']) if 'dynamic_w' in props else False,
        'dynamic_h': bool(props['dynamic_h']) if 'dynamic_h' in props else False,
        'show_usage': bool(props['show_usage']) if 'show_usage' in props else True,
        'disable_zoom': bool(props['disable_zoom']) if 'disable_zoom' in props else False,
    }

    rendered = ar.ascii_render(scene, color, w, h, aspect, ortho, fov, znear, zfar, 0.0)

    return params, rendered
