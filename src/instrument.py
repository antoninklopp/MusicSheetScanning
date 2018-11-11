from src.key import Key
from src.rectangle import Rectangle

class Instrument:

    def __init__(self, number, name="", number_times_per_bars=3):
        """
        Initializing instrument class
        """
        self.number = number
        self.name = name
        self.keys = []
        self.notes = []
        self.bars = []
        self.current_key = Key(Rectangle(0, 0, 0, 0), "g")
        self.number_times_per_bars = number_times_per_bars

    def change_key(self, new_key):
        """
        Change key during instrument class
        """
        self.keys.append(new_key)

    def add_notes(self, notes, bars):
        """
        Add notes
        """
        self.notes += notes
        self.bars += bars

    def check_notes(self, notes):
        """
        Returns a string representing check notes
        """
        print("number notes", len(notes))
        total = 0
        for note in notes:
            total += 4/note.sym

        if total != self.number_times_per_bars:
            print("Problem")
            if total > self.number_times_per_bars:
                print("Too much notes, strange")
            else:
                if self.number_times_per_bars - total == 0.5:
                    for i in range(len(notes) - 1):
                        if notes[i].sym == 4 and notes[i + 1].sym == 8: # Looking for patterns
                            pass

        return_notes = " "

        for note in notes:
            return_notes += note.lilypond_notation(self.current_key.name) + " "

        return return_notes + " "


    def get_lilypond_output(self):
        """
        Get the lilypond output of this instrument
        """

        print("INSTRUMENT", self.number, len(self.notes))

        lilypond_output = "instrument" + chr(97 + self.number) + " = \\new Voice { \n"
        if len(self.keys) == 0:
            print("No keys found, default is g")
            lilypond_output += Key(Rectangle(0, 0, 0, 0), "g").get_lilypond_output() + "\n"
        else:
            lilypond_output += self.key[0].get_lilypond_output() + "\n"

        lilypond_output += "\\time 3/4\n"

        note_index = 0
        bars_index = 0
        key_index = 1
        current_notes = []

        while note_index < len(self.notes) and bars_index < len(self.bars):
            if len(self.keys) > key_index and self.keys[key_index].rec.middle < self.notes[note_index].rec.middle:
                # Here we change key
                self.current_key = self.keys[key_index]
                self.key_index += 1
            if self.notes[note_index].rec.middle < self.bars[bars_index].middle:
                current_notes.append(self.notes[note_index])
                note_index += 1
            else:
                lilypond_output += self.check_notes(current_notes)
                bars_index += 1
                current_notes = []

        lilypond_output += "}\n"
        return lilypond_output