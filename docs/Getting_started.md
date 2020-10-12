# Getting Started

## Installation

Clone the repository. Install the required dependencies, you might want to install those into an virutalenv or a conda environment.

<span style="color:red">TODO: Add correct git url</span>

```python
git clone ...
cd energy_management_panel
pip install -r requirements.txt
```

It should now be possible to start the demo version of the EMP with:

```
cd source
./manage.py runserver
```

You can now inspect a demo UI build with the EMP framwork by opening [http://localhost:8000](http://localhost:8000):
![emp_demo_welcome](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_welcome.png)

## EMP Components and Functionality

The EMP consists of a title bar on the top, a nav bar on the left and white space that is used to display the page content. The title bar contains a place for a logo on the left, the title in the middle and the current time on the right. It is possible to configure logo and title in [emp_main/settings.py](../source/emp_main/settings.py). The nav bar always contains the necessary items for authentication, i.e. the Login/Logout buttons of which only the Login button is shown as the user is not authenticated yet, and one collapsible Group per installed UI app. For more technical information about the implementation of UI apps please see the example code at [source/emp_demo_ui_app](../source/emp_demo_ui_app/)

The demo contains only one UI  app with the name "Demo UI App". Each UI app may provide multiple pages, which can be accessed by clicking on the app name in the navbar. Now click on "Demo UI App" and then on "1 - Page space to continue".

![emp_demo_page_space](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_page_space.png)

Each page can populate a defined space of the EMP with content. This space is shown in yellow in the screenshot above. When developing pages it is a good idea to keep the pages content to this marked area. If that is not possible, scrolling is ok. 
The EMP is designed to be mobile friendly. The same page will look like this on a cheap mobile phone:

<img src="/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_page_space_mobile.png" alt="emp_demo_page_space_mobile" style="zoom: 50%;" />

The navbar is hidden on mobiles by default to save space and can be activated by clicking on the hamburger button:

<img src="/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_page_space_mobile_with_menu.png" alt="emp_demo_page_space_mobile_with_menu" style="zoom:50%;" />

When developing pages we suggest do apply a responsive design, e.g. by using [Bootsrap](https://github.com/twbs/bootstrap) that is already used by EMP. We especially promote to check a page design with the following settings:

* A cheap mobile in with 320 x 568 pixels (in landscape and portrait mode)
* A middle class tablet with 1024 x 768 pixels (at least in portrait mode)
* A modern desktop PC with 1920 x 1080 pixels (in portrait mode)

The EMP provides out of the box features for user authentication and access control. It is for example possible to provide some pages only for certain users. To present this first be aware that there is currently no page entry "2 - Permissions" nav bar. This is the case as the page has been restricted to be only visible for the test user. No click "Login" in the nav bar and use the following credentials:

| Username: | Password: |
| --------- | ---- |
| test | testuser |

After this you should be able to view the restricted page by clicking on "2 - Permissions" in the nav bar.

![emp_demo_permissions](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_permissions.png)

The permission system of the demo UI app has been implemented using the [django-guardian](https://github.com/django-guardian/django-guardian) package. The EMP provides an admin interface to control these permissions, beyond many other aspects of the data. In fact the core idea of the EMP is to provide pages that can be dynamically adjusted by configuring then in the admin page. In order to preceed first logout by clicking the "Logout" button in the nav bar. This should redirect you to the welcome page:![emp_demo_welcome](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_welcome.png)

In order to access the admin area visit http://localhost:8000/admin/ which will request a user/password combination.

![emp_demo_admin_login](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_login.png)

The admin user for this demo has the following credentials:

| Username: | Password: |
| --------- | --------- |
| admin     | admin     |

You should now see the root view of the admin space:

![emp_demo_admin_root](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_root.png)

The demo version of the EMP provides admin pages to configure the users (this is a django default), the datapoints (which we will visit later) and the pages of the demo UI app. Click on "Demo app pages" to see the internal representation of the pages.

![emp_demo_admin_demo_app_pages](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_demo_app_pages.png)

 It is worth noting that the demo UI app has been implemented in such way that every page corresponds to on entry in the database. Click on the "2 - Permissions" entry to view this object.

![emp_demo_admin_demo_app_page_permissions](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_demo_app_page_permissions.png)

The demoUI app uses the field "Page name" as entry within the nav bar and the "Page slug" to build the URL of the page. "Page content", "Page background color" and "Demo datapoint" are used to generate the content of the page. The user restrictions of the page can be seen by clicking on the "OBJECT PERMISSIONS" button directly under the top bar of the admin page.

![emp_demo_admin_demo_app_page_change_permissions](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_demo_app_page_change_permissions.png)

If you like you can change the current behaviour by filling in "AnonymousUser" (without quotes) into the text box (next to User identification) and click on "Manage user". Adding the "Can view demo app page" permission in the following dialogue would allow anybody (including non authenticated users) to access the restricted page.

![emp_demo_admin_demo_app_page_change_permissions_2](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_demo_app_page_change_permissions_2.png) 

Finally it should be noted that the exact behavior which page can be accessed by which user, including if such checking should be applied at all, depends on the implementation of the respective UI app. The implementation of the case here (using the django-guardian per object permission system) can be inspected in [source/emp_demo_ui_app/apps.py](../source/emp_demo_ui_app/apps.py).

Returning back to the intended application of the EMP, it is clear that a UI for interaction with a building will also need to display values emitted by hardware devices installed in that building to make sense. One may for example wish to implement a UI app with a page to display the current temperature of a room and allow users to modify the setpoint. In order to retrieve measurements and send actuator signals to hardware devices in buildings it is necessary to implement a "Datapoint interface" that takes care of this communication. Source code of a dummy interface that pushes random data into the EMP is provided in [source/emp_demo_dp_interface](./source/emp_demo_dp_interface) as an example. Assuming that such an interface exists, all incoming and outgoing information are related to datapoints. A datapoint is thereby by definition one source/sink of information in the hardware, for example a room climate senor in an office building may measure temperature and humidity values and has thus two datapoints. Respectively, a setpoint value of a heating is a datapoint too. For more information about datapoints and the the corresponding dataformat see [docs/Data_format.md](Data_format.md) and the implementation of datapoints in [source/emp_main/models.py](../source/emp_main/models.py).

To now see the how datapoints can be used, return to the EMP demo app by opening http://localhost:8000/demo/3-datapoints/

![emp_demo_datapoints](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_datapoints.png)

The demo utilizes a datapoint interface (source code at [source/emp_demo_dp_interface](../source/emp_demo_dp_interface/)) that pushes random values to the show datapoint every 5 seconds. Please note that the shown value on the page is updated too, without the page being reloaded. This is one core feature of the EMP, the convenient integration and automatic update of datapoint values and metadata. To illustrate this effect visit the admin page http://localhost:8000/admin/emp_main/datapoint/2/change/ of the particular datapoint in a second window.

![emp_demo_admin_change_datapoint](/home/david/devl/HoLL-Therm/energy_management_panel/docs/imgs/emp_demo_admin_change_datapoint.png)

The "3 - Datapoints" page displays two fields of this datapoint, "Unit" and "Last value". You can change these fields if you like and see how it affects the page (don't forget to save to make the changes effective).