# coding: utf-8
import socket
import requests
import urlparse
import datetime
import logging
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from raven.contrib.django.models import client


logger = logging.getLogger(__name__)

# Create your models here.
class Keys(models.Model):
    """ Store keys that has access to system, related to a user """
    user = models.ForeignKey(User,related_name='keys')
    key = models.CharField(max_length=250)
    creation_data = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(default=None)
    active = models.BooleanField(default=False)

class URL(models.Model):
    """ Store URLS and last status

    user = Who requested for url status
    url = Url requested for status
    update_time = Time of last update in this model for site_ip, site_ip_type,
        web_server_name and status_code
    last_time_checked = Last time that this url was checked
    site_ip = IP of server
    hostname = Hostname based on URL
    web_server_name = Name of webserver used to host this url
    html_status_code = HTML Status code returned by request to url
    """
    user = models.ForeignKey(User,related_name='urls_status')
    url = models.CharField(max_length=250)
    update_time = models.DateTimeField(default=None,null=True)
    last_time_checked = models.DateTimeField(default=None,null=True)
    site_ip = models.CharField(max_length=15)
    site_fqdn = models.CharField(max_length=250)
    web_server_name = models.CharField(max_length=100) # nginx, etc
    html_status_code = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user','url')

    def __unicode__(self):
       return " - ".join([self.url,str(self.html_status_code)])

    def update_status(self):
        try:
            logger.info(u"Checking url %s for user %s.",self.url,self.user.username)

            url = urlparse.urlparse(self.url)
            self.hostname = url.hostname
            if self.hostname:
                self.site_ip = socket.gethostbyname(self.hostname)
                self.site_fqdn = socket.getfqdn(self.hostname)
            request = requests.get(self.url)
            self.web_server_name = request.headers.get('server','')
            self.html_status_code = request.status_code

            self.last_time_checked = timezone.now()

            old = URL.objects.get(pk=self.pk)

            # some field is different, update
            if self.site_ip != old.site_ip or \
                    self.site_fqdn != old.site_fqdn or \
                    self.web_server_name != old.web_server_name or \
                    self.html_status_code != old.html_status_code:
                logger.info(u"Updating url %s for user %s.",self.url,self.user.username)
                self.update_time = self.last_time_checked

                # create a new history entry
                self.history.create(
                    update_time = self.update_status,
                    site_ip = self.site_ip,
                    site_fqdn = self.site_fqdn,
                    web_server_name = self.web_server_name,
                    html_status_code = self.html_status_code
                )

            self.save()
        except Exception as err:
            client.captureException()


class URLStatusHistory(models.Model):
    """ Store status changes (IP, Server Type, Status Code) """
    url = models.ForeignKey(URL,related_name='history')
    update_time = models.DateTimeField(auto_now_add=True)
    site_ip = models.CharField(max_length=15)
    site_fqdn = models.CharField(max_length=250)
    web_server_name = models.CharField(max_length=100) # nginx, etc
    html_status_code = models.IntegerField(default=0)
