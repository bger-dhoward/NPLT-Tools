__title__ = "Unhide NPLT\nElements"
__doc__ = "Unhide all NPLT Text, Detail Lines, and Dimensions in the active project"
__author__ = "D. Howard, Ballinger"

from Autodesk.Revit.DB import *
from System.Collections.Generic import List, IList
from pyrevit import revit, DB
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document

NPLT_notes = [n for n in FilteredElementCollector(doc).OfClass(TextNote) if "NPLT" in n.Name]
NPLT_lines = [e for e in FilteredElementCollector(doc).OfClass(CurveElement) if type(e) == DetailLine and "NPLT" in e.LineStyle.Name]
NPLT_dims = [d for d in FilteredElementCollector(doc).OfClass(Dimension) if d.Category.Name == "Dimensions" and "NPLT" in d.Name]

views = {}

for n in NPLT_notes:
    if n.OwnerViewId.IntegerValue not in views:
        views[n.OwnerViewId.IntegerValue] = List[ElementId]([n.Id])
    else:
        views[n.OwnerViewId.IntegerValue].Add(n.Id)

for elem in NPLT_lines:
    if elem.OwnerViewId.IntegerValue not in views:
        views[elem.OwnerViewId.IntegerValue] = List[ElementId]([elem.Id])
    else:
        views[elem.OwnerViewId.IntegerValue].Add(elem.Id)

for d in NPLT_dims:
    if d.OwnerViewId.IntegerValue not in views:
        views[d.OwnerViewId.IntegerValue] = List[ElementId]([d.Id])
    else:
        views[d.OwnerViewId.IntegerValue].Add(d.Id)

num_notes = len(NPLT_notes)
num_lines = len(NPLT_lines)
num_dims = len(NPLT_dims)
num_views = len(views)

description =   "NPLT elements unhidden in {v} views:\n" \
                            "    Notes: {num_notes}\n" \
                            "    Lines: {num_lines}\n" \
                            "    Dims:  {num_dims}".format(num_notes = num_notes, v = num_views, num_lines=num_lines, num_dims=num_dims)

if num_views > 0:
    t = Transaction(doc, "Unhide NPLT Elements")
    t.Start()

    for view_id, elem_list in views.items():
        view = doc.GetElement(ElementId(view_id))
        view.UnhideElements(elem_list)

    t.Commit()
    
    
    forms.alert(description, 
        sub_msg="This may include elements not already hidden. Use `Unhide NPLT` to show hidden elements", 
        title="Unhide NPLT Elements",
        ok=True,
        footer='Ballinger pyRevit Tools')

else:
    forms.alert("No Hideable NPLT elements found.", 
        title="Unhide NPLT Elements",
        ok=True,
        footer='Ballinger pyRevit Tools')
