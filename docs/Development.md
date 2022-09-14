# Development

Contributions and pull requests are welcome. Please revise the following before getting your hands dirty.

## Implementation Rules

Here additional rules for for implementations in specific programming languages.

### Python

Please follow these guidelines while implementing components in Python:

* **Readability counts! Thus, before you start:** Read and understand [PEP 8](https://www.python.org/dev/peps/pep-0008/).
* **Documentation is Key:** Try to document <u>why</u> stuff is done. Furthermore document <u>what</u> is done if that is not obvious from the code. 
* **Docstrings:** Every function/method/class should have a Docstring following the [Numpy convention](https://numpydoc.readthedocs.io/en/latest/format.html).
* **Provide tests for everything:** Tests ensure that your code can be maintained and is not thrown away after the first bug is encountered. Unless you have very good reason, use [pytest](https://docs.pytest.org/).
* **Use the right format:** Use [Black](https://github.com/psf/black) to format your code. Maximum line length is 80 characters.

Code will only be accepted to merge if it is:

* **Formally correct:** [Flake8](https://flake8.pycqa.org/en/latest/) shows no errors or warnings. Again using a maximum line length of 80 characters.
* **Logically correct:** All tests pass and all relevant aspects of the code are tested.

## Spinning up a development instance

On a Linux system you can start developing on the code quickly by following these steps.

* In a terminal execute:

  ```bash
  docker-compose down -v && USER_ID=$(id -u) GROUP_ID=$(id -g) docker-compose up --build
  ```

  Note that this command is identical to the command that was used to spin up the demo in [Getting Started](Getting_started.md). Note further that if you the `DJANGO_DEBUG` environment variable is set to `TRUE`, the development server will automatically reload on file changes on your local disk.

* For automatic execution of tests run the following in a second terminal:

  ```bash
  docker exec -it emp-devl auto-pytest /source/emp/
  ```

  Note that this will autoreload too, but you might want to be more precise about what tests should be executed by changing the `/source/emp/` to something more detailed, e.g. `/source/emp/emp_main` to only execute tests in the `emp_main` module.

* For an interactive python terminal execute:

  ```bash
  docker exec -it emp-devl /opt/conda/bin/python /source/emp/manage.py shell
  ```

## Further useful stuff

### Creating a Fixture for the Demo setup.

Use:

```bash
docker exec -it emp-devl /opt/conda/bin/python /source/emp/manage.py dumpdata --indent=4 auth.user guardian emp_main emp_demo_ui_app --natural-foreign > demo_data.json
```

