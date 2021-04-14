# The FZI Energy Management Panel (EMP) 

Building energy management (BEM) can be understood as the algorithmic optimization of the energy consumption patterns of buildings regarding energy efficiency and/or flexibility. However, in order to compute the optimal operational strategy, it is necessary to assess the demand of the users that must be fulfilled by the building. Such interaction between humans and the energy management system can be achieved by utilization of web based user interfaces, which is especially cost effective due to the omnipresence of computers and mobile device in modern societies. The EMP project has been designed and developed to reduce the necessary effort to implement such user interfaces. At its heart it follows a modular approach and consists of several independent components that can be combined to a user interface that matches the need of a concrete use case, which is not limited to energy management scenarios. Furthermore, it is easily possible to extend the EMP with self written components that are called apps. In order to keep such implementations as effective as possible, the EMP builds up on the [Django](https://www.djangoproject.com/) web framework, as the latter already provides many relevant functionality for such applications.

The EMP is the outcome of the continuous research on algorithmic energy management at the FZI Research Center for Information Technology, in particular the devision Intelligent Information and Communication in Technical Systems (IIK). Many concepts of the EMP are inspired by a previous implementation, also named Energy Management Panel, that has been developed by Birger Becker and that is documented in ["Interaktives Gebäude-Energiemanagement"](https://publikationen.bibliothek.kit.edu/1000043519).

## Documentation

**First things first: All documentation assumes that you are familiar at least with the basics of the Django web development framework. If this is not the case for you, please work through the offical [docs of the project](https://docs.djangoproject.com/) (at least the tutorial) or consult the excellent [Practical Django 2 and Channels 2](https://www.springer.com/de/book/9781484240984) book by Federico Marani.**

* An introduction to the EMP, including installation, can be found in [docs/Getting_started.md](./docs/Getting_started.md).
* Additional documentation is provided in the [docs](./docs) folder.
* The source code of the "Demo UI app" shown in the [docs/Getting_started.md](./docs/Getting_started.md) is provided in [source/emp_demo_ui_app](./source/emp_demo_ui_app). The source code is extensively commented and serves as a best practice for developing UI apps.
* In order to retrieve measurements and send actuator signals to hardware devices in buildings it is necessary to implement a "Datapoint interface" that takes care of this communication. Source code of a dummy interface that pushes random data into the EMP is provided in [source/emp_demo_dp_interface](./source/emp_demo_dp_interface) as an example.
* The EMP ships with an stand alone authenticator module that allows user management and authentication, that is used in the demo, and for which source code is placed in [source/emp_django_authenticator](./source/emp_django_authenticator/). Integration of the EMP into existing authentication infrastructure (e.g. LDAP) should be easily possible, see the source code of the provided authenticator as example. 

## Contact

Please feel free to contact [David Wölfle](https://www.fzi.de/en/about-us/organisation/detail/address/david-woelfle/) for all inquiries.

## Copyright and license

Code is copyright to the FZI Research Center for Information Technology and released under the MIT license. This repository also contains copies of source code released by the [Bootstrap](https://github.com/twbs/bootstrap), [D3](https://github.com/d3/d3), [JQuery](https://github.com/jquery/jquery) and [Popper JS](https://github.com/popperjs/popper-core) projects, which are copyright to the respective authors and released under the licenses listed in these repositories. A copy of these licenses is provided in  [LICENSE_LIBRARIES](LICENSE_LIBRARIES).