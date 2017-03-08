# renderer/html.py - Renders to HTML5 statute
import re
from .base import Renderer
from io import StringIO
from utils import normalize_spaces

class HtmlRenderer(Renderer):

    def render(self, act, buf=None):
        self.buf = buf or StringIO()
        self.buf.write('''<html lang="zh-Hant">
<head>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="styles/common.css" />
    <link rel="stylesheet" href="styles/print.css" media="print" />
    <link rel="stylesheet" href="styles/screen.css" media="screen" />
</head>
<body>\n''')
        self.render_act(act)
        self.buf.write('</body>\n</html>')
        return self.buf

    def render_act(self, act):
        buf = self.buf
        buf.write('<article class="act">\n')
        buf.write('<header>')
        buf.write(act.name)
        buf.write('</header>\n')
        buf.write('<ol class="history">\n')
        for h in act.history:
            buf.write('<li>')
            h = h.replace('中華民國', '民國').replace('學生代表大會', '學代會')
            h = normalize_spaces(h)
            h = re.sub('(（編按：[^）]+）)', r'<span class="note">\1</span>', h)
            buf.write(h)
            if h[-1] not in '>）)。':  # Consider <span> as well
                buf.write('。')
            buf.write('</li>\n')
        buf.write('</ol>\n')
        super().render_act(act)
        buf.write('</article>')

    def render_text(self, text):
        buf = self.buf
        buf.write('<p>')
        buf.write(text)
        buf.write('</p>\n')

    def render_chapter(self, chapter):
        buf = self.buf
        grade = 4 if '章' in chapter.number else 5
        buf.write('<h{grade}>{number}　{caption}</h{grade}>\n'.format(grade=grade, **chapter.__dict__))

    def render_article(self, article):
        buf = self.buf
        single_p = (len(article.subitems) == 1)
        buf.write('<h6 data-number="')
        buf.write(re.sub(r'^第([〇ㄧ一二三四五六七八九十]+)條(之[〇ㄧ一二三四五六七八九十]+)?', r'\1\2', article.number))
        buf.write('">')
        buf.write(article.number)
        if article.caption:
            buf.write('<span class="caption">（')
            buf.write(article.caption)
            buf.write('）</span>')
        if single_p and re.match(r'^[（\(]刪除[\)）]', article.subitems[0].caption):
            buf.write('\u200b<span class="caption deleted">（刪除）</span></h6>\n')
            return  # Short circuit
        buf.write('</h6>\n')
        if single_p:
            buf.write('<p>')
            buf.write(normalize_spaces(article.subitems[0].caption))
            buf.write('</p>\n')
        else:
            buf.write('<ol class="paragraphs">')
            super().render_article(article)
            buf.write('</ol>\n')

    def render_paragraph(self, paragraph):
        buf = self.buf
        buf.write('<li>')
        buf.write(normalize_spaces(paragraph.caption))
        buf.write('</li>\n')
        if paragraph.subitems:
            buf.write('<ol class="subsections">\n')
            super().render_paragraph(paragraph)
            buf.write('</ol>\n')

    def render_subsection(self, subsection):
        buf = self.buf
        caption = re.sub(r'^[〇ㄧ一二三四五六七八九十]+、\s*', '', subsection.caption)
        buf.write('<li>')
        buf.write(normalize_spaces(caption))
        buf.write('</li>\n')
        if subsection.subitems:
            buf.write('<ol class="items">\n')
            super().render_subsection(subsection)
            buf.write('</ol>\n')

    def render_item(self, item):
        buf = self.buf
        item = re.sub(r'^\([〇ㄧ一二三四五六七八九十]+\)\s*', '', item)
        buf.write('<li>')
        buf.write(normalize_spaces(item))
        buf.write('</li>\n')
