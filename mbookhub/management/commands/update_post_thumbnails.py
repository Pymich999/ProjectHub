# update_post_thumbnails.py
from django.core.management.base import BaseCommand
from mbookhub.models import Post

class Command(BaseCommand):
    help = 'Update thumbnails for existing posts with their book thumbnail'

    def handle(self, *args, **kwargs):
        posts_updated = 0
        for post in Post.objects.filter(thumbnail__isnull=True):
            if post.book.thumbnail:  # Only update if book has a thumbnail
                post.thumbnail = post.book.thumbnail
                post.save()
                posts_updated += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {posts_updated} posts with thumbnails.'))
