__title__ = "Hide NPLT\nElements"
__doc__ = "Hide all NPLT Text, Detail Lines, and Dimensions in the active project"
__author__ = "D. Howard, Ballinger"

from Autodesk.Revit.DB import *
from System.Collections.Generic import List, IList
from pyrevit import revit, DB
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document

NPLT_notes = [n for n in FilteredElementCollector(doc).OfClass(TextNote) if "NPLT" in n.Name and n.ViewSpecific]
NPLT_lines = [e for e in FilteredElementCollector(doc).OfClass(CurveElement) if type(e) == DetailLine and "NPLT" in e.LineStyle.Name and e.ViewSpecific]
NPLT_dims = [d for d in FilteredElementCollector(doc).OfClass(Dimension) if d.Category.Name == "Dimensions" and "NPLT" in d.Name and d.ViewSpecific]
NPLT_tags = [t for t in FilteredElementCollector(doc).OfClass(IndependentTag) if "NPLT" in t.Name and t.ViewSpecific]

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

for t in NPLT_tags:
    if t.OwnerViewId.IntegerValue not in views:
        views[t.OwnerViewId.IntegerValue] = List[ElementId]([t.Id])
    else:
        views[t.OwnerViewId.IntegerValue].Add(t.Id)

num_notes = len(NPLT_notes)
num_lines = len(NPLT_lines)
num_dims = len(NPLT_dims)
num_tags = len(NPLT_tags)
num_views = len(views)

description =   "NPLT elements in {v} views:\n" \
                            "    Notes: {num_notes}\n" \
                            "    Lines: {num_lines}\n" \
                            "    Dims:  {num_dims}\n" \
                            "    Tags:  {num_tags}".format(num_notes = num_notes, v = num_views, num_lines=num_lines, num_dims=num_dims, num_tags=num_tags)

owned_by_others = []

if num_views > 0:
    t = Transaction(doc, "Hide NPLT Elements")
    t.Start()

    for view_id, elem_list in views.items():
        if WorksharingUtils.GetCheckoutStatus(doc, ElementId(view_id)) != CheckoutStatus.OwnedByOtherUser:
            view = doc.GetElement(ElementId(view_id))
            view.HideElements(elem_list)
            if len(view.GetDependentViewIds()) > 0:
                for dependent_id in view.GetDependentViewIds():
                    if WorksharingUtils.GetCheckoutStatus(doc, dependent_id) != CheckoutStatus.OwnedByOtherUser:
                        d_view = doc.GetElement(dependent_id)
                        d_view.HideElements(elem_list)
                    else:
                        tip = WorksharingUtils.GetWorksharingTooltipInfo(doc, dependent_id)
                        owner = tip.Owner
                        viewname = doc.GetElement(dependent_id).Name
                        num_items = len(elem_list)
                        info = "{viewname}\n|  {num_items} elements \n|  owner: {owner}\n".format(viewname=viewname, num_items=num_items, owner=owner)
                        owned_by_others.append(info)
        else:
            tip = WorksharingUtils.GetWorksharingTooltipInfo(doc, ElementId(view_id))
            owner = tip.Owner
            viewname = doc.GetElement(ElementId(view_id)).Name
            num_items = len(elem_list)
            info = "{viewname}\n|  {num_items} elements \n|  owner: {owner}\n".format(viewname=viewname, num_items=num_items, owner=owner)
            owned_by_others.append(info)

    t.Commit()
    
    if len(owned_by_others) > 0:
        view_alert = "\n".join(owned_by_others)
        view_alert = "---------------------\n\nThe following views are currently checked out by another user and cannot be modified:\n\n" + view_alert
    else:
        view_alert = ""

    forms.alert(description, 
        sub_msg="This may include elements already hidden. Use `Unhide NPLT` to show hidden elements.\n" + view_alert, 
        title="Hide NPLT Elements",
        ok=True,
        footer='Ballinger pyRevit Tools')

else:
    forms.alert("No Hideable NPLT elements found.", 
        title="Unhide NPLT Elements",
        ok=True,
        footer='Ballinger pyRevit Tools')
