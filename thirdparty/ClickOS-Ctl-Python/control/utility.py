# -*- coding: utf-8 -*-

def inform(logger, message):
  logger.debug("💬  || {}".format(message))

def success(logger, message):
  logger.debug("☑️  || {}".format(message))