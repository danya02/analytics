from database import *
import ipaddress

class User:
    def __init__(self, request):
        uid = request.cookies.get('user_id')
        dnt_header = str(request.headers.get('dnt'))=='1'
        dnt_cookie = request.cookies.get('no-track') == '1'
        
#        if dnt_header:
#            self.user = self.get_dntheader_user()
        if dnt_cookie:
            self.user = self.get_dntcookie_user()
        else:
            try:
                self.user = UserModel.get(UserModel.uid == uid)
            except UserModel.DoesNotExist:
                self.user = UserModel.create()

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
        return {'user_id': self.user.uid, 'no-track': '0'}

    @staticmethod
    def anonymize_ip(ip_addr):
        # only works on ipv4 addresses. sets last 2 octets to zero.
        ip = ipaddress.ip_address(ip_addr)
        a,b,c,d = str(ip).split('.')
        return f'{a}.{b}.0.0'

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
