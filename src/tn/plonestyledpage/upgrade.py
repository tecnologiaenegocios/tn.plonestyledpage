from Acquisition import aq_parent
from Acquisition import aq_base
from plone.dexterity.content import Item
from Products.CMFCore.utils import getToolByName
from tn.plonestyledpage.styled_page import StyledPage

import logging


PACKAGE_NAME = 'tn.plonestyledpage'
PROFILE_ID   = 'profile-%s:default' % PACKAGE_NAME


def change_styled_page_class_to_custom_class(context, logger=None):
    """Method to get all styled pages and change their class from Dexterity's
    default to a customized version.
    """

    logger = _get_logger(logger)
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(portal_type='tn.plonestyledpage.styled_page')

    for brain in results:
        obj = brain.getObject()
        if isinstance(obj, Item) and not isinstance(obj, StyledPage):
            container = aq_parent(obj)

            id = obj.getId()
            path = brain.getPath()
            base = aq_base(obj)

            container._delObject(id)
            aq_base(obj).__class__ = StyledPage
            container._setObject(id, base)
            logger.info('Changed class of %s' % path)

    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile('profile-plone.app.intid:default',
                                   'intid-register-content')


def _get_logger(logger=None):
    if logger is None:
        return logging.getLogger(PACKAGE_NAME)
    return logger
