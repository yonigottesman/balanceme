


class FileParser(object):

    def factory(file):
        #TODO do something with this circular imports, whats the best practice here?
        from .visacal import VisaCalParser
        return VisaCalParser()
    factory = staticmethod(factory)

    #TODO make this abstract
    def get_transactions(self):
        pass




