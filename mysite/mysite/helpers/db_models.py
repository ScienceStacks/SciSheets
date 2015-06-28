'''Helpers for database models'''
from django.db import  models, connection
from django.core.management import sql, color

# Dynamic creation of a database model
# For now, assume that fields are char 50 so that fields is a list of strings
def create_model(name, field_names=None, module='', options=None, admin_opts=None):
  """
  Create specified model
  """
  class Meta:
    # Using type('Meta', ...) gives a dictproxy error during model creation
    pass

  # app_label must be set using the Meta inner class
  app_label = "app_%s" % name
  setattr(Meta, 'app_label', app_label)

  # Update Meta with any options that were provided
  if options is not None:
    for key, value in options.iteritems():
      setattr(Meta, key, value)

  # Set up a dictionary to simulate declarations within a class
  attrs = {'__module__': module, 'Meta': Meta}

  # Add in any fields that were provided
  fields = {}
  for name in field_names:
    fields.update({name: models.CharField(max_length=50)})
  if fields:
    attrs.update(fields)

  # Create the class, which automatically triggers ModelBase processing
  model = type(name, (models.Model,), attrs)

  # Create an Admin class if admin options were provided
  if admin_opts is not None:
    class Admin(admin.ModelAdmin):
      pass
    for key, value in admin_opts:
      setattr(Admin, key, value)
    admin.site.register(model, Admin)

  return model

def install(model):
  # Standard syncdb expects models to be in reliable locations,
  # so dynamic models need to bypass django.core.management.syncdb.
  # On the plus side, this allows individual models to be installed
  # without installing the entire project structure.
  # On the other hand, this means that things like relationships and
  # indexes will have to be handled manually.
  # This installs only the basic table definition.

  # disable terminal colors in the sql statements
  style = color.no_style()

  cursor = connection.cursor()
  statements, pending = sql.sql_model_create(model, style)
  for sql in statements:
    cursor.execute(sql)
