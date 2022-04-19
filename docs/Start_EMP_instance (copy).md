#  TODO

Add some hints about steps that must be done after starting with a new db --> makemigrations, migrate, createsuperuser



```
django-admin startproject yourname-main
```



* Copy settings to main folder

* ./manage.py startapp yourname-app

* Modify settings to your needs.

  * Add the new app to the EMP_APPS
  * Change WSGI Application (The ASGI application too if you want to use additional websockets etc.)
  * Check the DB settings, default is a SQLite

* Static files or templates that should be used in many apps can be stored in the main folder. You must add apps.py file and add the path to INSTALLED_APPS in settings file to allow django finding these files.

  ```
  from django.apps import AppConfig
  
  class ViewBwMain(AppConfig):
      name = 'view_bw_main'
  ```

  

