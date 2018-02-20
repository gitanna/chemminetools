from django.db import models

# Create your models here.

class Drug_targets_org(models.Model):

    target_drugs = models.TextField()
    uniprot_id = models.TextField()
    organism = models.TextField()

    class Meta:
        managed = True
        app_label = 'drugbank'



    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Drug_targets_org._meta.fields]

    def get_field(self, name):
        return getattr(self, name)

    def __unicode__(self):
        return '%s', (self.target_drugs)


class Ensb_uniport(models.Model):

    ensemble_id = models.TextField()
    uniprot_id = models.TextField()

    class Meta:
        managed = True
        app_label = 'drugbank'

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Ensb_uniport._meta.fields]

    def get_field(self, name):
        return getattr(self, name)


    def __unicode__(self):
        return '%s' ,self.ensemble_id
