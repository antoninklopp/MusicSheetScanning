from src.key import Key
from src.rectangle import Rectangle
from src.time_indication import TimeIndication

class Instrument:

    def __init__(self, number, name=""):
        """
        Initializing instrument class
        """
        self.number = number
        self.name = name
        self.notes = []
        self.bars = []
        self.current_key = None
        self.keys = []
        self.current_time_indication = None
        self.time_indications = []

    def change_key(self, new_key):
        """
        Change key during instrument class
        """
        if new_key is not None:
            if self.current_key is None:
                new_key.note_before = len(self.notes)
                self.current_key = new_key
                self.keys.append(new_key)
            elif (new_key.name != self.current_key.name):
                new_key.note_before = len(self.notes)
                self.current_key = new_key
                self.keys.append(new_key)

    def change_time_indication(self, new_time_indication):
        """
        Change the time indication of the instrument class
        """
        if new_time_indication is not None:
            print(new_time_indication, self.current_time_indication)
            if self.current_time_indication is None:
                new_time_indication.note_before = len(self.notes)
                self.current_time_indication = new_time_indication
                self.time_indications.append(new_time_indication)
            elif (new_time_indication.name != self.current_time_indication.name):
                new_time_indication.note_before = len(self.notes)
                self.current_time_indication = new_time_indication
                self.time_indications.append(new_time_indication)

    def add_notes(self, notes, bars):
        """
        Add notes
        """
        self.notes += notes
        self.bars += bars

    def get_current_key(self):
        return self.current_key

    def check_notes(self, notes):
        """
        Returns a string representing check notes
        """
        total = 0
        for note in notes:
            total += 4/note.sym

        if total != self.current_time_indication.get_times():
            # print("Problem")
            if total > self.current_time_indication.get_times():
                print("Too much notes, strange")
            elif len(notes) == 1:
                notes[0].add_time(total - 4/self.notes[0].sym)
            else:
                if self.current_time_indication.get_times() - total == 0.5:
                    for i in range(len(notes) - 1):
                        if notes[i].sym == 4 and notes[i + 1].sym == 8: # Looking for patterns
                            notes[i].add_time(0.5)

        return_notes = " "

        print("NEW BAR")

        for note in notes:
            return_notes += note.lilypond_notation(self.current_key) + " "
            print(note)

        print("total", total)

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
            print("KEY", self.keys[0].name)
            lilypond_output += self.keys[0].get_lilypond_output() + "\n"

        if len(self.time_indications) == 0:
            self.time_indications.append(TimeIndication(Rectangle(0, 0, 0, 0), "4_4"))
            lilypond_output += self.time_indications[0].get_lilypond_output() + "\n"
            self.current_time_indication = self.time_indications[0]

        note_index = 0
        bars_index = 0
        key_index = 1
        time_index = 1
        current_notes = []

        print("nombres de clés différentes", len(self.keys))
        print("nombre de changement de mesures", self.time_indications)

        while note_index < len(self.notes) and bars_index < len(self.bars):
            if len(self.keys) > key_index and note_index > self.keys[key_index].note_before \
                and self.keys[key_index].rec.middle[0] < self.notes[note_index].rec.middle[0]:
                # We first flush the output
                # Then we can change key
                lilypond_output += self.check_notes(current_notes)
                bars_index += 1
                current_notes = []
                # Here we change key
                self.current_key = self.keys[key_index]
                key_index += 1
            if len(self.time_indications) > time_index and note_index > self.time_indications[time_index].note_before \
                and self.time_indications[time_index].rec.middle[0] < self.notes[note_index].rec.middle[0]:
                # We first flush the output. 
                # Then we can change time indication
                lilypond_output += self.check_notes(current_notes)
                lilypond_output += self.time_indications[time_index].get_lilypond_output()
                print("NEW TIME INDICATION \n\n\n")
                bars_index += 1
                current_notes = []
                self.current_time_indication = self.time_indications[time_index]
                time_index += 1
            if self.notes[note_index].rec.middle[0] < self.bars[bars_index].middle[0]:
                current_notes.append(self.notes[note_index])
                note_index += 1
            else:
                lilypond_output += self.check_notes(current_notes)
                bars_index += 1
                current_notes = []

        lilypond_output += self.check_notes(current_notes)

        lilypond_output += "}\n"
        return lilypond_output