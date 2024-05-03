from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Updates Subscription Status'
    
    def handle(self, *args, **options):
        # Get all users with a subscription
        users_with_subscription = User.objects.filter(expired=False)
        # print(users_with_subscription)
        for user in users_with_subscription:
            if user.subscription_due_date != None:
                if timezone.now() > user.subscription_due_date :  
                    user.subscription_status = 'EXPIRED'
                    user.expired = True
                    user.save()
      
            self.stdout.write(self.style.SUCCESS('Subscription status updated successfully'))
                
        