# EMP Evaluation System

This is the source of the evaluation system app. This porjects intorduces mulitple features for monitoring and analyzing building energy management data. Furthermore, a comparison tool was included. This tool enables users to compare different building energy management optimization algoithms or differen algorithm settings. 
Overall this module's goal is to point out the potential of energy management algorithms to inexperienced users and help experts to develop new optimization algorithms with the help of the data monitoring features of this module. 

## Application Idea

The application is build in a content management style. Users may create system evaluation pages with the help of Django's admin pages. These evaluation page's then will be build up on frontend load. This enables users to creat their own building energy management dashboards. 
Predefined user interface elements are available. These UI elements can be linked to Datapoint objects and, therefore, will be filled with the Datapoint's information.

## Development
This module was developed as a Computer Scinece Bachelor's thesis by [Lukas Landwich](https://github.com/LukasLandwich/). For further development information, background knowledge or if interested feel free to read the [thesis](Bachelorarbeit_Lukas_Landwich.pdf) or to contact [me](https://github.com/LukasLandwich/) or my supervisor [David Wölfle](https://github.com/david-woelfle).

## Implementation
The implementation is following the basic Django project setup. Therefore, only outstanding implementation desicions will be introduced in the following.

### admin.py
To provide the content management system like structure of the admin panel the nested admin Django extension is used. Therefore, any number of andmin inline formes may be stacked.

### test.py
At the moment there are no tests available. They are in development and will be published as soon as possible.

### static/emp_evaluation_system
This folder contains all static files. Most imporant the JavaScript files that contain the data fetch and update logic. Also the metric compution functions are defined in these JavaScript files.

### templates/emp_evaluation_system
This folder holds all Django HTML templates. On page load the [Evaluation System Page Template](templates/emp_evaluation_system/evaluationSystemPage.html) is required. From here on the user configured page objects are recursivly traversed and the right templates will be included.