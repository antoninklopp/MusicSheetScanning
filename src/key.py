
class Key:
    def __init__(self, rec, name="g"):
        self.rec = rec
        self.name = name
        self.middle = rec.y + (rec.h / 2.0)
        self.note_before = 0

    def get_lilypond_output(self):
        if self.name == "g":
            return "\\clef treble"
        elif self.name == "f":
            return "\\clef bass"
        elif self.name == "c3":
            return "\\clef alto"
        else:
            print("Not implemented", self.name)
            raise

    def __str__(self):
        return "key " + self.name

    def note_before(self, number):
        self.note_before = number