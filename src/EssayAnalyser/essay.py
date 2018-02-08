class Essay:
    """ Wrapper for the essay handling """

    def __init__(self, txt: str):
        self.text = txt
        self.data = {}
        self.meta = {}

    def process(self):

        self.data['text'] = self.text
        return self

