# Development

Here some hints that support development of the EMP.

## Creating a Fixture for the Demo setup.

Use:

```bash
docker exec -it emp-devl /opt/conda/bin/python /source/emp/manage.py dumpdata --indent=4 auth.user guardian emp_main emp_demo_ui_app --natural-foreign > demo_data.json
```

