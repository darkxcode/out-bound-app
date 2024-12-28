from django.db import models

from apps.campaigns.models import Recipient


class Spreadsheet(models.Model):
    campaign = models.OneToOneField('campaigns.Campaign', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='spreadsheets')

    def save(self, **kwargs):
        self.full_clean()
        super().save(**kwargs)
        new_structure, created = Structure.objects.get_or_create(spreadsheet=self)
        self.structure = new_structure
        self.structure.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'spreadsheet'
        verbose_name_plural = 'spreadsheets'


class Cell(models.Model):
    spreadsheet = models.ForeignKey(Spreadsheet, related_name='cells', on_delete=models.CASCADE)
    row = models.PositiveSmallIntegerField()
    column = models.PositiveSmallIntegerField()
    content = models.CharField(max_length=255)

    def __str__(self):
        return self.content[:50]

    class Meta:
        ordering = ('row', 'column')
        verbose_name = 'Cell'
        verbose_name_plural = 'Cells'


class Structure(models.Model):
    spreadsheet = models.OneToOneField(Spreadsheet, on_delete=models.CASCADE)
    email = models.OneToOneField(Cell, null=True, on_delete=models.CASCADE)
    first_name = models.OneToOneField(Cell, blank=True, null=True, related_name='first_name', on_delete=models.CASCADE)
    last_name = models.OneToOneField(Cell, blank=True, null=True, related_name='last_name', on_delete=models.CASCADE)
    company_name = models.OneToOneField(Cell, blank=True, null=True, related_name='company_name', on_delete=models.CASCADE)
    snippet_1 = models.OneToOneField(Cell, blank=True, null=True, related_name='snippet_1', on_delete=models.CASCADE)
    snippet_2 = models.OneToOneField(Cell, blank=True, null=True, related_name='snippet_2', on_delete=models.CASCADE)
    snippet_3 = models.OneToOneField(Cell, blank=True, null=True, related_name='snippet_3', on_delete=models.CASCADE)

    def save(self, **kwargs):
        self.spreadsheet.recipients.only('pk').delete()
        rows = {cell.row for cell in self.spreadsheet.cells.all()}
        for row in rows:
            new_recipient_data = dict()
            for cell in self.spreadsheet.cells.filter(row=row):
                if hasattr(self.email, 'column') and cell.column == self.email.column:
                    new_recipient_data['email'] = cell.content
                if hasattr(self.first_name, 'column') and cell.column == self.first_name.column:
                    new_recipient_data['first_name'] = cell.content
                if hasattr(self.last_name, 'column') and cell.column == self.last_name.column:
                    new_recipient_data['last_name'] = cell.content
                if hasattr(self.company_name, 'column') and cell.column == self.company_name.column:
                    new_recipient_data['company_name'] = cell.content
                if hasattr(self.snippet_1, 'column') and cell.column == self.snippet_1.column:
                    new_recipient_data['snippet_1'] = cell.content
                if hasattr(self.snippet_2, 'column') and cell.column == self.snippet_2.column:
                    new_recipient_data['snippet_2'] = cell.content
                if hasattr(self.snippet_3, 'column') and cell.column == self.snippet_3.column:
                    new_recipient_data['snippet_3'] = cell.content

            if new_recipient_data.get('email', False) and '@' in new_recipient_data['email']:    # Simple validation ;)
                Recipient.objects.update_or_create(
                    campaign=self.spreadsheet.campaign,
                    spreadsheet=self.spreadsheet,
                    **new_recipient_data
                )
        super().save(**kwargs)

    def __str__(self):
        return f'Structure of "{self.spreadsheet.name}" spreadsheet.'

    class Meta:
        verbose_name = 'Structure'
        verbose_name_plural = 'Structures'
