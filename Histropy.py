from InterHist import InterHist
import easygui

# 1. Prompts user to select image.
path = easygui.fileopenbox()
# 2. Opens InterHist Object, running preliminary calculations and opening the Histropy window.
ih = InterHist(path)

