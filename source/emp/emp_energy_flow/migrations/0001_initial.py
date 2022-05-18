# Generated by Django 3.2.12 on 2022-05-18 20:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('emp_main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnergyFlow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Energy Flow, will be displayed in the Nav menu.', max_length=18, unique=True)),
                ('slug', models.SlugField(help_text='The name of the energy flow page used in the URL of it. Must be unique as two pages of this app cannot have the same url.', unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Will not display Energy Flow if False.')),
            ],
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The Name of the Widget displayed in the header of the card. ', max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Will not display widget and corresponding flows if False.')),
                ('icon_url', models.CharField(help_text='The (relative) URL of the the icon to display for the card. ', max_length=200)),
                ('grid_position_left', models.PositiveIntegerField(help_text='The left coordinate of the card in the grid (grid-row-start)')),
                ('grid_position_right', models.PositiveIntegerField(help_text='The right coordinate of the card in the grid (grid-row-end)')),
                ('grid_position_top', models.PositiveIntegerField(help_text='The top position of the card in the grid (grid-column-start)')),
                ('grid_position_bottom', models.PositiveIntegerField(help_text='The bottom position of the card in the grid (grid-column-end)')),
                ('datapoint1_label', models.CharField(blank=True, default='', help_text='The label that is displayed in the Energy Flow Page to describe the first datapoint.', max_length=50)),
                ('datapoint1_color', models.CharField(choices=[('elec', 'Electricity'), ('heat', 'Heat'), ('cold', 'Cold'), ('ngas', 'Natural Gas')], default='heat', help_text='The color schema used to display the value of the first datapoint in the progress bar.', max_length=4)),
                ('datapoint1_show_progressbar', models.BooleanField(default=True, help_text='Will not display the progressbar for datapoint if False.')),
                ('datapoint1_progressbar_reverse', models.BooleanField(default=False, help_text='Will display the progressbar load reversed if True. This is e.g. usefull for a cold storage, that is full when close to min_value.')),
                ('datapoint2_label', models.CharField(blank=True, default='', help_text='The label that is displayed in the Energy Flow Page to describe the second datapoint.', max_length=50)),
                ('datapoint2_color', models.CharField(choices=[('elec', 'Electricity'), ('heat', 'Heat'), ('cold', 'Cold'), ('ngas', 'Natural Gas')], default='heat', help_text='The color schema used to display the value in the progress bar.', max_length=4)),
                ('datapoint2_show_progressbar', models.BooleanField(default=True, help_text='Will not display the progressbar for datapoint if False.')),
                ('datapoint2_progressbar_reverse', models.BooleanField(default=False, help_text='Will display the progressbar load reversed if True. This is e.g. usefull for a cold storage, that is full when close to min_value.')),
                ('datapoint1', models.ForeignKey(blank=True, default=None, help_text='The first datapoint corresponding to the value that is displayed in the Energy Flow Page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datapoint1', to='emp_main.datapoint')),
                ('datapoint2', models.ForeignKey(blank=True, default=None, help_text='The second datapoint corresponding to the value that is displayed in the Energy Flow Page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datapoint2', to='emp_main.datapoint')),
                ('energyflow', models.ForeignKey(blank=True, help_text='The EnergyFlow page the widget belongs to. Not displayed if null.', null=True, on_delete=django.db.models.deletion.CASCADE, to='emp_energy_flow.energyflow')),
            ],
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flow_color', models.CharField(choices=[('elec', 'Electricity'), ('heat', 'Heat'), ('cold', 'Cold'), ('ngas', 'Natural Gas')], default='heat', help_text='The color schema used for the flow.', max_length=4)),
                ('energyflow', models.ForeignKey(help_text='The EnergyFlow page the Flow belongs to. Not displayed if null.', null=True, on_delete=django.db.models.deletion.CASCADE, to='emp_energy_flow.energyflow')),
                ('origin_device', models.ForeignKey(help_text='The widget the energy flow starts (for a positive sign).', on_delete=django.db.models.deletion.CASCADE, related_name='origin_widget', to='emp_energy_flow.widget')),
                ('target_device', models.ForeignKey(help_text='The widget the energy flow ends (for a positive sign).', on_delete=django.db.models.deletion.CASCADE, related_name='target_widget', to='emp_energy_flow.widget')),
                ('value_datapoint', models.ForeignKey(blank=True, default=None, help_text='The datapoint which value is used to compute the movement speed.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='emp_main.datapoint')),
            ],
        ),
    ]
