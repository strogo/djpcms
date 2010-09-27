# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'InnerTemplate'
        db.create_table('djpcms_innertemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('blocks', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djpcms', ['InnerTemplate'])

        # Adding model 'CssPageInfo'
        db.create_table('djpcms_csspageinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('body_class_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('container_class_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('fixed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('gridsize', self.gf('django.db.models.fields.PositiveIntegerField')(default=12)),
        ))
        db.send_create_signal('djpcms', ['CssPageInfo'])

        # Adding model 'Page'
        db.create_table('djpcms_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('application', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('redirect_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='redirected_from', null=True, to=orm['djpcms.Page'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('url_pattern', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('inner_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djpcms.InnerTemplate'], null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('in_navigation', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('cssinfo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djpcms.CssPageInfo'], null=True, blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('requires_login', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('soft_root', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['djpcms.Page'])),
            ('code_object', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('doctype', self.gf('django.db.models.fields.PositiveIntegerField')(default=4)),
            ('insitemap', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('djpcms', ['Page'])

        # Adding model 'BlockContent'
        db.create_table('djpcms_blockcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='blockcontents', to=orm['djpcms.Page'])),
            ('block', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('plugin_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('arguments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('container_type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('djpcms', ['BlockContent'])

        # Adding unique constraint on 'BlockContent', fields ['page', 'block', 'position']
        db.create_unique('djpcms_blockcontent', ['page_id', 'block', 'position'])

        # Adding model 'SiteContent'
        db.create_table('djpcms_sitecontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user_last', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('code', self.gf('djpcms.fields.SlugCode')(unique=True, max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
        ))
        db.send_create_signal('djpcms', ['SiteContent'])

        # Adding model 'AdditionalPageData'
        db.create_table('djpcms_additionalpagedata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additionaldata', to=orm['djpcms.Page'])),
            ('where', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djpcms', ['AdditionalPageData'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'BlockContent', fields ['page', 'block', 'position']
        db.delete_unique('djpcms_blockcontent', ['page_id', 'block', 'position'])

        # Deleting model 'InnerTemplate'
        db.delete_table('djpcms_innertemplate')

        # Deleting model 'CssPageInfo'
        db.delete_table('djpcms_csspageinfo')

        # Deleting model 'Page'
        db.delete_table('djpcms_page')

        # Deleting model 'BlockContent'
        db.delete_table('djpcms_blockcontent')

        # Deleting model 'SiteContent'
        db.delete_table('djpcms_sitecontent')

        # Deleting model 'AdditionalPageData'
        db.delete_table('djpcms_additionalpagedata')


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
        'djpcms.additionalpagedata': {
            'Meta': {'object_name': 'AdditionalPageData'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additionaldata'", 'to': "orm['djpcms.Page']"}),
            'where': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'djpcms.blockcontent': {
            'Meta': {'ordering': "('page', 'block', 'position')", 'unique_together': "(('page', 'block', 'position'),)", 'object_name': 'BlockContent'},
            'arguments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'block': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'container_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blockcontents'", 'to': "orm['djpcms.Page']"}),
            'plugin_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'djpcms.csspageinfo': {
            'Meta': {'object_name': 'CssPageInfo'},
            'body_class_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'container_class_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fixed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gridsize': ('django.db.models.fields.PositiveIntegerField', [], {'default': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'djpcms.innertemplate': {
            'Meta': {'object_name': 'InnerTemplate'},
            'blocks': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'template': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'djpcms.page': {
            'Meta': {'object_name': 'Page'},
            'application': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'code_object': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cssinfo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djpcms.CssPageInfo']", 'null': 'True', 'blank': 'True'}),
            'doctype': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'inner_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djpcms.InnerTemplate']", 'null': 'True', 'blank': 'True'}),
            'insitemap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['djpcms.Page']"}),
            'redirect_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirected_from'", 'null': 'True', 'to': "orm['djpcms.Page']"}),
            'requires_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'soft_root': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'url_pattern': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'djpcms.sitecontent': {
            'Meta': {'ordering': "('code',)", 'object_name': 'SiteContent'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'code': ('djpcms.fields.SlugCode', [], {'unique': 'True', 'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'user_last': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['djpcms']
