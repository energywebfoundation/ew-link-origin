import datetime
import inspect


class JSONAble(object):
    def to_dict(self):
        result = {}
        init = getattr(self, '__init__')
        for parameter in inspect.signature(init).parameters:
            att = getattr(self, parameter)
            if isinstance(att, list) or isinstance(att, set):
                att = [self.to_dict_or_self(o) for o in att]
            if isinstance(att, (datetime.datetime, datetime.date)):
                att = att.isoformat()
            result[parameter] = self.to_dict_or_self(att)
        return result

    @staticmethod
    def to_dict_or_self(obj):
        to_dict = getattr(obj, 'to_dict', None)
        if to_dict:
            return to_dict()
        else:
            return obj


class CEST(datetime.tzinfo):

    def __init__(self):
        self.ZERO = datetime.timedelta(0)
        self.TWO = datetime.timedelta(hours=2)

    def utcoffset(self, dt):
        return self.TWO

    def tzname(self, dt):
        return "CEST"

    def dst(self, dt):
        return self.TWO


class UTC(datetime.tzinfo):

    def __init__(self):
        self.ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO