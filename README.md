# Personal blog site written in Python and Django

This is my website hosted on [blaz.is](https://blaz.is). It is meant to be used just by me, but it does have support for multiple authors. User-facing side is pretty much finished, apart from comments, and RSS feed. Author-facing side still needs improvements (account pages, markdown editor, etc.).

Feel free to use it anyhow you want, in. Well, in accordance to GPL v3 :)

## Enabling interactive asciirend

Go to [`asciirend`](https://github.com/h33p/asciirend) repo, run `build_extras.sh`, and symlink the resulting `pkg` directory to `index/static/js/modules`. Re-run collectstatic, and you should be good to go.
