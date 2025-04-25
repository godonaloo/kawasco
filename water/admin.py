from django.contrib import admin
from water.models import User, WaterInstallationApplication,Complaint

# List of all the models you want to register
models = [User, WaterInstallationApplication,Complaint]

# Loop through the models and register them in the admin site
for model in models:
    admin.site.register(model)
