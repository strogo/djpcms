# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FlowItem'
        db.create_table('flowrepo_flowitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.TextField')()),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('visibility', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('tags', self.gf('tagging.fields.TagField')(default='', max_length=2500, blank=True)),
            ('allow_comments', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('source_id', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('object_str', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('flowrepo', ['FlowItem'])

        # Adding unique constraint on 'FlowItem', fields ['content_type', 'object_id']
        db.create_unique('flowrepo_flowitem', ['content_type_id', 'object_id'])

        # Adding M2M table for field authors on 'FlowItem'
        db.create_table('flowrepo_flowitem_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('flowitem', models.ForeignKey(orm['flowrepo.flowitem'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('flowrepo_flowitem_authors', ['flowitem_id', 'user_id'])

        # Adding M2M table for field groups on 'FlowItem'
        db.create_table('flowrepo_flowitem_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('flowitem', models.ForeignKey(orm['flowrepo.flowitem'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('flowrepo_flowitem_groups', ['flowitem_id', 'group_id'])

        # Adding model 'CategoryType'
        db.create_table('flowrepo_categorytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('flowrepo', ['CategoryType'])

        # Adding model 'Category'
        db.create_table('flowrepo_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=260, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowrepo.CategoryType'])),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='crl', max_length=3, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['Category'])

        # Adding model 'Report'
        db.create_table('flowrepo_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=260, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='crl', max_length=3, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['flowrepo.Report'])),
        ))
        db.send_create_signal('flowrepo', ['Report'])

        # Adding model 'Bookmark'
        db.create_table('flowrepo_bookmark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=260, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('extended', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('thumbnail_url', self.gf('django.db.models.fields.URLField')(max_length=1000, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['Bookmark'])

        # Adding model 'Image'
        db.create_table('flowrepo_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=260, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('elem_url', self.gf('django.db.models.fields.URLField')(max_length=1000, blank=True)),
            ('elem', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['Image'])

        # Adding model 'Gallery'
        db.create_table('flowrepo_gallery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=260, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['Gallery'])

        # Adding model 'GalleryImage'
        db.create_table('flowrepo_galleryimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['flowrepo.Image'])),
            ('gallery', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['flowrepo.Gallery'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('flowrepo', ['GalleryImage'])

        # Adding model 'Attachment'
        db.create_table('flowrepo_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=260, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('elem_url', self.gf('django.db.models.fields.URLField')(max_length=1000, blank=True)),
            ('elem', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['Attachment'])

        # Adding model 'Message'
        db.create_table('flowrepo_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['Message'])

        # Adding M2M table for field links on 'Message'
        db.create_table('flowrepo_message_links', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('message', models.ForeignKey(orm['flowrepo.message'], null=False)),
            ('contentlink', models.ForeignKey(orm['flowrepo.contentlink'], null=False))
        ))
        db.create_unique('flowrepo_message_links', ['message_id', 'contentlink_id'])

        # Adding model 'ContentLink'
        db.create_table('flowrepo_contentlink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('flowrepo', ['ContentLink'])

        # Adding model 'FlowRelated'
        db.create_table('flowrepo_flowrelated', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['flowrepo.FlowItem'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('flowrepo', ['FlowRelated'])

        # Adding unique constraint on 'FlowRelated', fields ['item', 'content_type', 'object_id']
        db.create_unique('flowrepo_flowrelated', ['item_id', 'content_type_id', 'object_id'])

        # Adding model 'WebAccount'
        db.create_table('flowrepo_webaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('e_data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tags', self.gf('tagging.fields.TagField')(default='', max_length=2500, blank=True)),
        ))
        db.send_create_signal('flowrepo', ['WebAccount'])

        # Adding unique constraint on 'WebAccount', fields ['name', 'user']
        db.create_unique('flowrepo_webaccount', ['name', 'user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'WebAccount', fields ['name', 'user']
        db.delete_unique('flowrepo_webaccount', ['name', 'user_id'])

        # Removing unique constraint on 'FlowRelated', fields ['item', 'content_type', 'object_id']
        db.delete_unique('flowrepo_flowrelated', ['item_id', 'content_type_id', 'object_id'])

        # Removing unique constraint on 'FlowItem', fields ['content_type', 'object_id']
        db.delete_unique('flowrepo_flowitem', ['content_type_id', 'object_id'])

        # Deleting model 'FlowItem'
        db.delete_table('flowrepo_flowitem')

        # Removing M2M table for field authors on 'FlowItem'
        db.delete_table('flowrepo_flowitem_authors')

        # Removing M2M table for field groups on 'FlowItem'
        db.delete_table('flowrepo_flowitem_groups')

        # Deleting model 'CategoryType'
        db.delete_table('flowrepo_categorytype')

        # Deleting model 'Category'
        db.delete_table('flowrepo_category')

        # Deleting model 'Report'
        db.delete_table('flowrepo_report')

        # Deleting model 'Bookmark'
        db.delete_table('flowrepo_bookmark')

        # Deleting model 'Image'
        db.delete_table('flowrepo_image')

        # Deleting model 'Gallery'
        db.delete_table('flowrepo_gallery')

        # Deleting model 'GalleryImage'
        db.delete_table('flowrepo_galleryimage')

        # Deleting model 'Attachment'
        db.delete_table('flowrepo_attachment')

        # Deleting model 'Message'
        db.delete_table('flowrepo_message')

        # Removing M2M table for field links on 'Message'
        db.delete_table('flowrepo_message_links')

        # Deleting model 'ContentLink'
        db.delete_table('flowrepo_contentlink')

        # Deleting model 'FlowRelated'
        db.delete_table('flowrepo_flowrelated')

        # Deleting model 'WebAccount'
        db.delete_table('flowrepo_webaccount')


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
        'flowrepo.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'elem': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'elem_url': ('django.db.models.fields.URLField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '260', 'blank': 'True'})
        },
        'flowrepo.bookmark': {
            'Meta': {'object_name': 'Bookmark'},
            'extended': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '260', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'thumbnail_url': ('django.db.models.fields.URLField', [], {'max_length': '1000', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        'flowrepo.category': {
            'Meta': {'object_name': 'Category'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'crl'", 'max_length': '3', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '260', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowrepo.CategoryType']"})
        },
        'flowrepo.categorytype': {
            'Meta': {'object_name': 'CategoryType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'flowrepo.contentlink': {
            'Meta': {'object_name': 'ContentLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'flowrepo.flowitem': {
            'Meta': {'ordering': "['-timestamp']", 'unique_together': "[('content_type', 'object_id')]", 'object_name': 'FlowItem'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.TextField', [], {}),
            'object_str': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'source_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''", 'max_length': '2500', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'visibility': ('django.db.models.fields.IntegerField', [], {'default': '3'})
        },
        'flowrepo.flowrelated': {
            'Meta': {'unique_together': "(('item', 'content_type', 'object_id'),)", 'object_name': 'FlowRelated'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['flowrepo.FlowItem']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'flowrepo.gallery': {
            'Meta': {'object_name': 'Gallery'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '260', 'blank': 'True'})
        },
        'flowrepo.galleryimage': {
            'Meta': {'ordering': "('order',)", 'object_name': 'GalleryImage'},
            'gallery': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['flowrepo.Gallery']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['flowrepo.Image']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'flowrepo.image': {
            'Meta': {'object_name': 'Image'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'elem': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'elem_url': ('django.db.models.fields.URLField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '260', 'blank': 'True'})
        },
        'flowrepo.message': {
            'Meta': {'object_name': 'Message'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['flowrepo.ContentLink']", 'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'flowrepo.report': {
            'Meta': {'object_name': 'Report'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'crl'", 'max_length': '3', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['flowrepo.Report']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '260', 'blank': 'True'})
        },
        'flowrepo.webaccount': {
            'Meta': {'unique_together': "(('name', 'user'),)", 'object_name': 'WebAccount'},
            'e_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''", 'max_length': '2500', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['flowrepo']
