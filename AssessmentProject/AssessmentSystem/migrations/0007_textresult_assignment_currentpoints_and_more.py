# Generated by Django 4.1.5 on 2023-04-30 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AssessmentSystem', '0006_rename_qtype_qtypes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='textresult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sigmin', models.IntegerField(default=0, help_text='Result of test in points, lower bound')),
                ('sigmax', models.IntegerField(default=0, help_text='Result of test in points, upper bound')),
                ('description', models.CharField(default='There is no description for this number of points yet.', help_text='Description of achievements', max_length=7168)),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='currentpoints',
            field=models.IntegerField(default=0, help_text='Result of test in points'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='resultready',
            field=models.BooleanField(default=0, help_text='Test passed but dont calculated'),
        ),
        migrations.AddField(
            model_name='results',
            name='answerID',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='AssessmentSystem.answers'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='qtypeID',
            field=models.IntegerField(default=0, help_text='Type of question'),
        ),
        migrations.AddField(
            model_name='results',
            name='value',
            field=models.CharField(default='0', help_text='Answer', max_length=255),
        ),
    ]
