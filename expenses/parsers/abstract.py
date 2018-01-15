


class FileParser(object):

    def factory(file):
        #TODO do something with this circular imports, whats the best practice here?
        from .visacal import VisaCalParser, is_visacal

        if is_visacal(file):
            return VisaCalParser()

    factory = staticmethod(factory)

    #TODO make this abstract
    def get_transactions(self):
        pass




