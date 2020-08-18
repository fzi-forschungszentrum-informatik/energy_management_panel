# The FZI Energy Management Panel (EMP) 

Building energy management (BEM) can be understood as the algorithmic optimization of the energy consumption patterns of buildings regarding energy efficiency and/or flexibility. However, in order to compute the optimal operational strategy, it is necessary to assess the demand of the users that must be fulfilled by the building. Such interaction between humans and the energy management system can be achieved by utilization of web based user interfaces, which is especially cost effective due to the omnipresence of computers and mobile device in modern societies. The EMP project has been designed and developed to reduce the necessary effort to implement such user interfaces. It is an outcome of the continuous research on algorithmic energy management at the FZI Research Center for Information Technology, in particular the devision Intelligent Information and Communication in Technical Systems (IIK)

## Quick start

Clone the repository. Install the required dependencies, you might want to install those into an virutalenv or a conda environment.

<span style="color:red">TODO: Add correct git url</span>

```python
git clone ...
cd energy_management_panel
pip install -r requirements.txt
```

Apply migrations and start the development server.

```
cd source
./manage.py makemigrions
./manage.py migrate
./manage.py runserver
```



## Contact

Please feel free to contact [David Wölfle](https://www.fzi.de/en/about-us/organisation/detail/address/david-woelfle/) for all inquiries.

## Copyright and license

Code is copyright to the FZI Research Center for Information Technology and released under the MIT license. This repository also contains copies of source code released by the [Bootsrap](https://github.com/twbs/bootstrap) and [JQuery](https://github.com/jquery/jquery) projects, which are copyright to the respective authors and released under the licenses listed in these repositories. 