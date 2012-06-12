from cssutils.css import CSSRule
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from tn.plonestyledpage import _
from zope.keyreference.interfaces import IKeyReference

import cssutils
import zope.schema


def getEscapedStyles(page):
    id = getUniqueId(page)
    css = cssutils.parseString(page.styles)
    for rule in css.cssRules:
        if not rule.type == CSSRule.STYLE_RULE:
            continue
        for selector in rule.selectorList:
            namespace, element = selector.element
            if namespace:
                # Change only elements within the default namespace.
                continue
            selector.selectorText = u"#%(id)s %(selector)s" % {
                'id': id, 'selector': selector.selectorText
            }
    return css.cssText

def getUniqueId(page):
    return 'page' + str(hash(IKeyReference(page)))


class IStyledPageSchema(form.Schema):

    body = RichText(
        title=_(u'Page body'),
        description=_(u'The contents of the page'),
    )

    styles = zope.schema.SourceText(
        title=_(u'Page styles'),
        description=_(u'Additional styles for this page.'),
        required=False
    )


class View(grok.View):
    grok.context(IStyledPageSchema)

    def id(self):
        return getUniqueId(self.context)

    def styles(self):
        return ('<style type="text/css" media="all">%s</style' %
                self.cdata_styles())

    def cdata_styles(self):
        return "/*<![CDATA[*/%s/*]]>*/" % self.escaped_styles()

    def escaped_styles(self):
        return getEscapedStyles(self.context)
