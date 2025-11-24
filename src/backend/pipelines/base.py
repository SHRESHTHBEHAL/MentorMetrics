class BaseProcessor:
    def process(self, data):
        raise NotImplementedError("Subclasses must implement process method")
