class TimeIndication:
    def __init__(self, rec, name="4_4"):
        self.rec = rec
        self.name = name
        self.middle = rec.y + (rec.h / 2.0)

    def get_lilypond_output(self):
        return "\\time " + "/".join(self.name.split("_"))

    def get_times(self):
        return int(self.name.split("_")[0]) * 4/int(self.name.split("_")[1])

    def __str__(self):
        return "time indication " + self.name