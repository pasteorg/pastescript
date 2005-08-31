"""
This module defines all the database objects for the application.
They are all based on SQLObject classes; attributes that are set to
things like StringCol are database columns, and the class name matches
the database name.

You can also use this file as a script, to create the necessary
tables.
"""

from mx import DateTime
from sqlobject import *
from paste import CONFIG
import string
import os
try:
    from ZPTKit.templatetools import ContextWrapper
except ImportError:
   # When we aren't being run in a web context
    pass

try:
    main_connection = connectionForURI(CONFIG['database'])
except:
    pass
main_connection._pool = None

sqlhub.processConnection = main_connection

def do_in_transaction(func, *args, **kw):
    conn = main_connection.transaction()
    sqlhub.threadConnection = conn
    try:
        try:
            value = func(*args, **kw)
        except:
            conn.rollback()
            raise
        else:
            conn.commit()
            return value
    finally:
        del sqlhub.threadConnection


######################################################################
### Tables
######################################################################

class MyTable(SQLObject):
    """
    MyTable decription.
    """
    class sqlmeta:
        defaultOrder = ['name',]
    name = StringCol(notNull=True, alternateID=True)
    description = StringCol(default=None)
    active = BoolCol(notNull=True, default=False)


# define order to create tables in when using sqlobject-admin
soClasses = [MyTable]

