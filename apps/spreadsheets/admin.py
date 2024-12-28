from django.contrib import admin
from apps.spreadsheets.models import Spreadsheet, Cell, Structure
from apps.spreadsheets.forms import SpreadsheetForm, StructureForm


@admin.register(Spreadsheet)
class SpreadsheetAdmin(admin.ModelAdmin):
    form = SpreadsheetForm

    def save_model(self, request, obj, form, change):
        instance = form.save()
        file = request.FILES.get('file', None)
        if file:    # Then we should save all cells to db.
            spreadsheet = file.get_sheet()
            for cell_y, row in enumerate(spreadsheet, start=1):
                for cell in row:
                    cell_x = row.index(cell)
                    Cell.objects.update_or_create(
                        spreadsheet=instance,
                        row=cell_y,
                        column=cell_x,
                        content=cell
                    )
        return super().save_model(request, obj, form, change)


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    form = StructureForm
