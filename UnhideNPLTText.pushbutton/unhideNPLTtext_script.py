__title__ = "Unhide\n NPLT Text"
__doc__ = "Unhide all NPLT Text in the active project"
__author__ = "D. Howard, Ballinger"

from Autodesk.Revit.DB import *
from System.Collections.Generic import List, IList
from pyrevit import revit, DB

doc = __revit__.ActiveUIDocument.Document

NPLT_notes = [n for n in FilteredElementCollector(doc).OfClass(TextNote) if "NPLT" in n.Name]

views = {}

for n in NPLT_notes:
    if n.OwnerViewId.ToString() not in views:
        views[n.OwnerViewId.IntegerValue] = List[ElementId]([n.Id])
    else:
        views[n.OwnerViewId.IntegerValue].Add(n.Id)

num_notes = len(NPLT_notes)
num_views = len(views)

transaction_description = "Unhide {n} NPLT notes in {v} views".format(n = num_notes, v = num_views)

t = Transaction(doc, transaction_description)
t.Start()

for view_id, note_list in views.items():
    view = doc.GetElement(ElementId(view_id))
    view.UnhideElements(note_list)

t.Commit()