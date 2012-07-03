# coding: utf8
import IPy
from django.db import models

class URLStatusHistory(models.Model):
    """ Store status changes (IP, Server Type, Status Code) """
    url = models.CharField(max_length=250)
    update_time = models.DateTimeField(null=True,default=None)
    site_ip = models.CharField(max_length=15,null=True,default=None)
    site_fqdn = models.CharField(max_length=250,null=True,default=None)
    web_server_name = models.CharField(max_length=100,null=True,default=None)
    html_status_code = models.IntegerField(null=True,default=None)

    def __unicode__(self):
        return self.url

    def get_ip_type(self):
        """
        Return ip type using IPy package. Possible types (until 27/06/2012)
        are:

        6TO4, ADMIN-LOCAL MULTICAST, ALLOCATED AFRINIC, ALLOCATED APNIC,
        ALLOCATED ARIN, ALLOCATED LACNIC, ALLOCATED RIPE NCC, BMWG,
        DOCUMENTATION, GLOBAL MULTICAST, GLOBAL-UNICAST, IPV4MAP, LINK-LOCAL
        MULTICAST, LINKLOCAL, LOOPBACK, MULTICAST, NODE-LOCAL MULTICAST,
        ORCHID, ORG-LOCAL MULTICAST, PREFIX-BASED MULTICAST, PRIVATE, PUBLIC,
        RESERVED, RESERVED MULTICAST, RP-EMBEDDED MULTICAST, SITE-LOCAL
        MULTICAST, SPECIALPURPOSE, TEREDO, ULA, UNASSIGNED, UNSPECIFIED,
        WKP46TRANS

        return '' if self.site_ip isn't filled.

        """
        if self.site_ip:
            return IPy.IP(self.site_ip).iptype()
        return ''