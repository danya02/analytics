from database import *
import ipaddress
import datetime

class User:
    def __init__(self, request):
        uid = request.cookies.get('user_id')
        dnt_header = str(request.headers.get('dnt'))=='1'
        dnt_cookie = request.cookies.get('no-track') == '1'
        self.has_consented = request.cookies.get('consent') == '1'
#        if dnt_header:
#            self.user = self.get_dntheader_user()
        if dnt_cookie:
            self.user = self.get_dntcookie_user()
        else:
            try:
                self.user = UserModel.get(UserModel.uid == uid)
            except UserModel.DoesNotExist:
                self.user = UserModel.create()
        self.ip = self.anonymize_ip(request.remote_addr)  # while IPs are not bound to users, the user object is only supposed to persist for one request, so it makes sense to keep this around.

    def __str__(self):
#        if self.is_dntheader_user:
#            return 'Using DNT header'
        if self.is_dntcookie_user:
            return 'Using DNT cookie'
        else:
            return 'User ID '+str(self.user.uid)

    @property
    def cookies(self):
#        if self.is_dntheader_user:
#            return {}
        if self.is_dntcookie_user:
            return {'no-track': '1'}
        return {'user_id': self.user.uid, 'no-track': '0', 'consent': self.has_consented}

    @staticmethod
    def anonymize_ip(ip_addr):
        # only works on ipv4 addresses. sets last 2 octets to zero.
        ip = ipaddress.ip_address(ip_addr)
        a,b,c,d = str(ip).split('.')
        return f'{a}.{b}.0.0'

    def add_visit(self, site_uid, endpoint_addr):
        try:
            site = Site.get(Site.uid == site_uid)
        except Site.DoesNotExist:
            raise FileNotFoundError('no such site with id', site_uid)

        try:
            endpoint = Endpoint.get(Endpoint.address == endpoint_addr, Endpoint.site == site)
        except Endpoint.DoesNotExist:
            endpoint = Endpoint.create(address=endpoint_addr, site=site)  # TODO: should this have protection against malicious addition of names?

        latest_user_visit = None
        try:
            latest_user_visit = Visit.select().join(Session).where(Session.user == self.user).order_by(Visit.date.desc()).get()
        except DoesNotExist:
            pass
        now = datetime.datetime.now()
        
        if latest_user_visit is not None and now.timestamp() - latest_user_visit.date.timestamp() < 15*60:  # visits less than 15 minutes apart are considered to be a part of the same session
            session = latest_user_visit.session
        else:
            session = Session.create(user=self.user)

        visit = Visit.create(endpoint=endpoint, ip=self.ip, session=session)
        return visit

#    @staticmethod
#    def get_dntheader_user():
#        try:
#            return UserModel.get(UserModel.uid == '00000000-0000-0000-0000-000000000000')
#        except UserModel.DoesNotExist:
#            return UserModel.create(uid='00000000-0000-0000-0000-000000000000')
#    
#    @property
#    def is_dntheader_user(self):
#        return self.user == self.get_dntheader_user()

    @staticmethod
    def get_dntcookie_user():
        try:
            return UserModel.get(UserModel.uid == 'ffffffff-ffff-ffff-ffff-ffffffffffff')
        except UserModel.DoesNotExist:
            return UserModel.create(uid='ffffffff-ffff-ffff-ffff-ffffffffffff')
    
    @property
    def is_dntcookie_user(self):
        return self.user == self.get_dntcookie_user()
