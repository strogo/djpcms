from datetime import datetime

from atomformat import Feed

from models import Report

class ReportFeed(Feed):
    feed_id      = "my_id"
    feed_title   = ""
    feed_updated = datetime.now()
    feed_description = ""
    
    def item_id(self, post):
        return '.'
    
    def item_title(self, post):
        return post.title
    
    def item_updated(self, post):
        return post.created
    
    def item_published(self, post):
        return post.publish
    
    def item_authors(self, item):
        for author in item.authors.all():
            person_dict = {'name': author.first_name}
            yield person_dict
            
    def item_content(self, item):
        content_dict = {}
        content_dict['type'] = 'html'
        content_text = item.htmlbody()
        return (content_dict,content_text)
    
    def item_links(self, item):
        return [{'href':item.url()}]
    
    def items(self):
        return Report.objects.filter(status = 2)
    