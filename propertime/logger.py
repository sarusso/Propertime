# -*- coding: utf-8 -*-
"""The library logger"""

import os
import logging

LOGLEVEL = os.environ.get('PROPERTIME_LOGLEVEL') if os.environ.get('PROPERTIME_LOGLEVEL') else 'CRITICAL'

levels_mapping = { 50: 'CRITICAL',
                   40: 'ERROR',
                   30: 'WARNING',
                   20: 'INFO',
                   10: 'DEBUG',
                    0: 'NOTSET'}
               

def setup(level=LOGLEVEL, force=False):
    propertime_logger = logging.getLogger('propertime')
    try:
        configured = False
        for handler in propertime_logger.handlers:
            if handler.get_name() == 'propertime_handler':
                configured = True
                if force:
                    handler.setLevel(level=level) # Set global propertime logging level
                    propertime_logger.setLevel(level=level) # Set global propertime logging level
                else:
                    if levels_mapping[handler.level] != level.upper():
                        propertime_logger.warning('You tried to setup the logger with level "{}" but it is already configured with level "{}". Use force=True to force reconfiguring it.'.format(level, levels_mapping[handler.level]))
    except IndexError:
        configured=False
    
    if not configured:
        propertime_handler = logging.StreamHandler()
        propertime_handler.set_name('propertime_handler')
        propertime_handler.setLevel(level=level) # Set propertime default (and only) handler level 
        propertime_handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
        propertime_logger.addHandler(propertime_handler)
        propertime_logger.setLevel(level=level) # Set global propertime logging level
