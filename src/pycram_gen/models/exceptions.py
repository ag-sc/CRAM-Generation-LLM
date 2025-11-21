# -*- coding: utf-8 -*-

class PrompterException(Exception):
    """
    Exception is raised if a designator generation ends abnormally
    (i.e., if the finish reason is not stop)
    """

    pass
