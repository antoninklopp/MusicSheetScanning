
class Key:
    def __init__(self, rec, name="g"):
        self.rec = rec
        self.name = name
        self.middle = rec.y + (rec.h / 2.0)

    def get_lilypond_output(self):
        if self.name == "g":
            return "\\clef treble"
        elif self.name == "f":
            return "\\clef bass"
        else:
            print("Not implemented")
            raise