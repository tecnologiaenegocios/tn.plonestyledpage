from cssutils.css import CSSRule
from five import grok
from plone.app.textfield import RichText
from plone.dexterity import content
from plone.directives import form
from plone.supermodel import model
from tn.plonestyledpage import _
from tn.ploneformwidget.sourcecode import SourceCodeFieldWidget
from zope.keyreference.interfaces import IKeyReference
from z3c.form import widget

import cssutils
import zope.interface
import zope.schema


def getStyleBlock(page):
    cdata_block = u"/*<![CDATA[*/%s/*]]>*/" % (page.styles or u'')
    return u'<style type="text/css" media="all">%s</style>' % cdata_block


def getEscapedStyleBlock(page):
    cdata_block = u"/*<![CDATA[*/%s/*]]>*/" % getEscapedStyles(page)
    return u'<style type="text/css" media="all">%s</style>' % cdata_block


def getEscapedStyles(page):
    if not page.styles:
        return u''
    id = getUniqueId(page)
    css = cssutils.parseString(page.styles)
    for rule in css.cssRules:
        if not rule.type == CSSRule.STYLE_RULE:
            continue
        for selector in rule.selectorList:
            selector.selectorText = u"#%(id)s %(selector)s" % {
                'id': id, 'selector': selector.selectorText
            }
    return css.cssText


def getUniqueId(page):
    return 'page' + str(hash(IKeyReference(page)))


class IStyledPageSchema(model.Schema):

    body = RichText(
        title=_(u'Page body'),
        description=_(u'The contents of the page'),
    )

    form.widget(styles=SourceCodeFieldWidget)
    styles = zope.schema.SourceText(
        title=_(u'Page styles'),
        description=_(u'Additional styles for this page.'),
        required=False
    )

    def transform_body():
        """Return the body output relative to the context.

        In other words, just use this method instead of body.output for the
        common cases.
        """


class StyledPage(content.Item):
    zope.interface.implements(IStyledPageSchema)

    body = None
    styles = None

    def transform_body(self):
        return self.body.output_relative_to(self)


class View(grok.View):
    grok.context(IStyledPageSchema)
    grok.require('zope2.View')

    def id(self):
        return getUniqueId(self.context)

    def styles(self):
        return getEscapedStyleBlock(self.context)


# This adapter is registered in ZCML under the name 'editor_mode'.
mode_adapter = widget.StaticWidgetAttribute(u'css',
                                            field=IStyledPageSchema['styles'])
