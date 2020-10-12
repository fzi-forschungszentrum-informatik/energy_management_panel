# EMP Demo UI app

This is the source of the demo app introduced in [docs/Getting_started.md](../../docs/Getting_started.md). Beyond presenting the basic functionality of the EMP, this app also serves as a best practice example for implementing new apps to extend the EMP. The content of this folder will be introduced in detail in following.

### admin.py

Defines the admin pages for the app. There is no difference to the default procedure of Django.

### apps.py

Holds all code that should be executed to startup of the app, which is none for this one, but be might be necessary. E.g. a datapoint integration app might need to connect to some backend or message broker.

Beyond this functionality any EMP app that provides pages to the user should provide the `app_url_prefix` object and the `get_app_nav_content_for_user` and `get_permitted_datapoint_ids_for_user` functions. These are used patch in the urls of the app, and to populate the navbar with the app pages and for automatic permission checking.

### migrations

No changes to the Django default usage. Avoid any migrations that need manual interaction, at least of you wish to share your app with others.

### models.py

No changes to the Django default usage. 

### static

Should contain the static components of the app, e.g. JS and CSS files or other static content like images and icons. It is good convention to place these in a folder that is named after the app, e.g. here [./static/emp-demo-ui-app/](./static/emp-demo-ui-app/), as this will prevent name collisions when Django collects the static content of all apps. Be aware that for the app name underscores have been replaced with dashes, as the folder will be a name of the URLs of the static content.

### templates

Pages of the UI apps will usually require a template to dynamically generate the html content. The templates of the Demo UI App page are located in the templates  [templates/emp_demo_ui_app](./templates/emp_demo_ui_app) folder. Be aware the the inner repetition of the app name ("emp_demo_ui_ap") is good convention to prevent name collisions between apps when loading templates in views.

### tests

Contains all automated tests of this app. We strongly suggest to apply test driven development (TDD) to generate sustainable code, and to provide tests for alle relevant python components, e.g. apps, models, views, signals and templatetags. See e.g. [here](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing) for a guide.

### urls.py

No changes to the Django default usage. 

### views.py

No changes to the Django default usage. Be aware that EMPBaseView exists in [source/emp_main/views.py](../emp_main/views.py) which should be inherited from to provide the general functionality of the EMP, like the content of nav bar or the permission checking system.