# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Keys'
        db.create_table('server_keys', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='keys', to=orm['auth.User'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('creation_data', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('valid_until', self.gf('django.db.models.fields.DateTimeField')(default=None)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('server', ['Keys'])

        # Adding model 'URL'
        db.create_table('server_url', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='urls_status', to=orm['auth.User'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(default=None)),
            ('last_time_checked', self.gf('django.db.models.fields.DateTimeField')(default=None)),
            ('site_ip', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('site_fqdn', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('web_server_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('html_status_code', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('server', ['URL'])

        # Adding unique constraint on 'URL', fields ['user', 'url']
        db.create_unique('server_url', ['user_id', 'url'])

        # Adding model 'URLStatusHistory'
        db.create_table('server_urlstatushistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history', to=orm['server.URL'])),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('site_ip', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('site_fqdn', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('web_server_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('html_status_code', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('server', ['URLStatusHistory'])


    def backwards(self, orm):
        # Removing unique constraint on 'URL', fields ['user', 'url']
        db.delete_unique('server_url', ['user_id', 'url'])

        # Deleting model 'Keys'
        db.delete_table('server_keys')

        # Deleting model 'URL'
        db.delete_table('server_url')

        # Deleting model 'URLStatusHistory'
        db.delete_table('server_urlstatushistory')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'server.keys': {
            'Meta': {'object_name': 'Keys'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'creation_data': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keys'", 'to': "orm['auth.User']"}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {'default': 'None'})
        },
        'server.url': {
            'Meta': {'unique_together': "(('user', 'url'),)", 'object_name': 'URL'},
            'html_status_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_time_checked': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'site_fqdn': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'site_ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urls_status'", 'to': "orm['auth.User']"}),
            'web_server_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'server.urlstatushistory': {
            'Meta': {'object_name': 'URLStatusHistory'},
            'html_status_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_fqdn': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'site_ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': "orm['server.URL']"}),
            'web_server_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['server']