from src.note import Note
from src.rectangle import Rectangle

def write_check_notes(notes, number_times_per_bars):
    # First we check that time is ok.

    if len(notes) == 0:
        print("PROBLEM HERE, no notes between two bars")

    total = 0
    for note in notes:
        total += 4/note.sym

    if total != number_times_per_bars:
        print("Problem")

    return_notes = []

    for note in notes:
        return_notes.append(note.lilypond_notation())
    
    return return_notes


def reconstruct_sheet(notes, bars, number_times_per_bars=4):
    """
    Reconstruct the sheet as a lilypond file
    """
    with open("output/sheet_reconstructed.ly", "a") as f:
        note_index = 0
        bars_index = 0
        current_notes = []
        while note_index < len(notes) or bars_index < len(bars):
            if notes[note_index].rec.x < bars[bars_index].x:
                current_notes.append(notes[note_index])
                note_index += 1
            else:
                bars_index += 1
                written_notes = write_check_notes(current_notes, number_times_per_bars)
                current_notes = []
                if written_notes is not None and len(written_notes) != 0:
                    print("debut")
                    f.write(" ".join(written_notes))
                    f.write("\n")
                    print("fin")
                break

    print("OK")