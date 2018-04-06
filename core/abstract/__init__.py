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