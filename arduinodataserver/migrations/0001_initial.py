# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MeterType'
        db.create_table('arduinodataserver_metertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('arduinodataserver', ['MeterType'])

        # Adding model 'Meter'
        db.create_table('arduinodataserver_meter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('meter_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['arduinodataserver.MeterType'])),
            ('default_interval', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='default_meter', null=True, to=orm['arduinodataserver.IntervalType'])),
            ('is_counter', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('arduinodataserver', ['Meter'])

        # Adding model 'MeterData'
        db.create_table('arduinodataserver_meterdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['arduinodataserver.Meter'])),
            ('meter_count', self.gf('django.db.models.fields.IntegerField')()),
            ('diff', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('arduinodataserver', ['MeterData'])

        # Adding model 'IntervalType'
        db.create_table('arduinodataserver_intervaltype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.IntegerField')()),
            ('unit_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('unit_fraction', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('backlog', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('force_recreate', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('arduinodataserver', ['IntervalType'])

        # Adding M2M table for field meter_set on 'IntervalType'
        db.create_table('arduinodataserver_intervaltype_meter_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('intervaltype', models.ForeignKey(orm['arduinodataserver.intervaltype'], null=False)),
            ('meter', models.ForeignKey(orm['arduinodataserver.meter'], null=False))
        ))
        db.create_unique('arduinodataserver_intervaltype_meter_set', ['intervaltype_id', 'meter_id'])

        # Adding model 'Interval'
        db.create_table('arduinodataserver_interval', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('total', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('average', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('interval_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['arduinodataserver.IntervalType'])),
            ('from_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('to_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('data_entries', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('arduinodataserver', ['Interval'])

        # Adding unique constraint on 'Interval', fields ['interval_type', 'from_time']
        db.create_unique('arduinodataserver_interval', ['interval_type_id', 'from_time'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Interval', fields ['interval_type', 'from_time']
        db.delete_unique('arduinodataserver_interval', ['interval_type_id', 'from_time'])

        # Deleting model 'MeterType'
        db.delete_table('arduinodataserver_metertype')

        # Deleting model 'Meter'
        db.delete_table('arduinodataserver_meter')

        # Deleting model 'MeterData'
        db.delete_table('arduinodataserver_meterdata')

        # Deleting model 'IntervalType'
        db.delete_table('arduinodataserver_intervaltype')

        # Removing M2M table for field meter_set on 'IntervalType'
        db.delete_table('arduinodataserver_intervaltype_meter_set')

        # Deleting model 'Interval'
        db.delete_table('arduinodataserver_interval')


    models = {
        'arduinodataserver.interval': {
            'Meta': {'unique_together': "(('interval_type', 'from_time'),)", 'object_name': 'Interval'},
            'average': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'data_entries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'from_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['arduinodataserver.IntervalType']"}),
            'to_time': ('django.db.models.fields.DateTimeField', [], {}),
            'total': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'arduinodataserver.intervaltype': {
            'Meta': {'object_name': 'IntervalType'},
            'backlog': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'force_recreate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meter_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['arduinodataserver.Meter']", 'symmetrical': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.IntegerField', [], {}),
            'unit_fraction': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'arduinodataserver.meter': {
            'Meta': {'object_name': 'Meter'},
            'default_interval': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'default_meter'", 'null': 'True', 'to': "orm['arduinodataserver.IntervalType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_counter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meter_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['arduinodataserver.MeterType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'arduinodataserver.meterdata': {
            'Meta': {'object_name': 'MeterData'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'diff': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['arduinodataserver.Meter']"}),
            'meter_count': ('django.db.models.fields.IntegerField', [], {})
        },
        'arduinodataserver.metertype': {
            'Meta': {'object_name': 'MeterType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['arduinodataserver']
