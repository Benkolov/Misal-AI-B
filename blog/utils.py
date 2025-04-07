from django.utils.safestring import mark_safe
import markdown
import bleach
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension

def render_markdown(content):
    # Разрешени HTML тагове
    allowed_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'a', 'ul', 'ol', 'li',
        'blockquote', 'code', 'pre', 'hr', 'br', 'div', 'span', 'img', 'table', 'thead',
        'tbody', 'tr', 'th', 'td'
    ]

    # Разрешени атрибути за HTML таговете
    allowed_attrs = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class'],
        'span': ['class'],
        '*': ['id', 'class']
    }

    # Разширения за Markdown
    extensions = [
        'markdown.extensions.extra',  # Включва tables, attr_list и др.
        'markdown.extensions.smarty',  # Умни кавички и тирета
        FencedCodeExtension(),  # Код в оградени блокове ```
        CodeHiliteExtension(css_class='highlight'),  # Оцветяване на синтаксиса
        'markdown.extensions.toc',  # Съдържание
        'markdown.extensions.nl2br',  # Нови редове като <br>
    ]

    # Конвертиране на Markdown в HTML
    html = markdown.markdown(content, extensions=extensions)

    # Почистване на HTML за сигурност
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=False)

    # Връщане на безопасен HTML
    return mark_safe(clean_html)
