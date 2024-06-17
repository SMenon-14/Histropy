from InterHist import InterHist
import easygui

# 1. Prompt user to select image

path = easygui.fileopenbox()
ih = InterHist(path, 1)

