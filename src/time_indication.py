class TimeIndication:
    def __init__(self, rec, name="4_4"):
        self.rec = rec
        self.name = name
        self.middle = rec.y + (rec.h / 2.0)
        self.note_before = 0

    def get_lilypond_output(self):
        return "\n \\time " + "/".join(self.name.split("_")) + "\n"

    def get_times(self):
        return int(self.name.split("_")[0]) * 4/int(self.name.split("_")[1])

    def __str__(self):
        return "time indication " + self.name + "\n" + self.rec.__str__()

    def note_before(self, number):
        self.note_before = number