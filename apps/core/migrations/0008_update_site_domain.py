from django.db import migrations
from django.conf import settings

def update_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # We use settings.SITE_ID which is usually 1
    site_id = getattr(settings, 'SITE_ID', 1)
    if Site.objects.filter(pk=site_id).exists():
        site = Site.objects.get(pk=site_id)
        site.domain = 'artistahub.com'
        site.name = 'Artistahub'
        site.save()
    else:
        Site.objects.create(pk=site_id, domain='artistahub.com', name='Artistahub')

def reverse_update_site_domain(apps, schema_editor):
    # Optional: Revert to example.com if unapplying migration, but usually not strictly necessary
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_explorerprofile_user_delete_artistprofile_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site_domain, reverse_update_site_domain),
    ]
