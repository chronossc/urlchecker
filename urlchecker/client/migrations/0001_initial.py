# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'URLStatusHistory'
        db.create_table('client_urlstatushistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('site_ip', self.gf('django.db.models.fields.CharField')(default=None, max_length=15, null=True)),
            ('site_fqdn', self.gf('django.db.models.fields.CharField')(default=None, max_length=250, null=True)),
            ('web_server_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, null=True)),
            ('html_status_code', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
        ))
        db.send_create_signal('client', ['URLStatusHistory'])


    def backwards(self, orm):
        # Deleting model 'URLStatusHistory'
        db.delete_table('client_urlstatushistory')


    models = {
        'client.urlstatushistory': {
            'Meta': {'object_name': 'URLStatusHistory'},
            'html_status_code': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_fqdn': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '250', 'null': 'True'}),
            'site_ip': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '15', 'null': 'True'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'web_server_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['client']