import re


class Policy(object):

    def __init__(self, etag='', version='', bindings=[]):
        self.etag = etag
        self.version = version
        self.bindings = []
        for binding_dict in bindings:
            binding = self.Binding.from_dict(self, binding_dict)
            self.bindings.append(binding)

    def from_dict(self, source):
        policy = Policy(etag=source[u'etag'],
                        version=source[u'version'],
                        bindings=source[u'bindings'])
        return policy

    def to_dict(self):
        dest = {
            u'etag': self.etag,
            u'version': self.version,
            u'bindings': [binding.to_dict() for binding in self.bindings]
        }
        return dest

    def to_list(self):
        dest = [{
            u'principal_type': m.principal_type,
            u'principal': m.principal,
            u'role': self.bindings.role,
        } for self.bindings in self.bindings for m in self.bindings.members]
        return dest

    def filter_bindings_by_type(self, type):
        type = type.lower()
        filtered_bindings = [
            b for b in self.bindings
            if any(m.principal_type.lower() == type for m in b.members)
        ]
        member_bindings = []
        for binding in filtered_bindings:
            binding.members = [
                m for m in binding.members if m.principal_type.lower() == type
            ]
            member_bindings.append(binding)
        self.bindings = member_bindings
        return self

    def filter_bindings_by_principal(self, principal):
        filtered_bindings = [
            b for b in self.bindings
            if any(m.principal == principal for m in b.members)
        ]
        member_bindings = []
        for binding in filtered_bindings:
            binding.members = [
                m for m in binding.members if m.principal == principal
            ]
            member_bindings.append(binding)
        self.bindings = member_bindings
        return self

    def principals(self):
        return [
            m.member
            for self.bindings in self.bindings
            for m in self.bindings.members
        ]

    def roles(self):
        return [
            self.bindings.role
            for self.bindings in self.bindings
            for m in self.bindings.members
        ]

    def filter_bindings_by_domain(self, domain):
        # TODO: disallow service accounts
        filtered_bindings = [
            b for b in self.bindings if any(
                m.principal.endswith(domain) for m in b.members)
        ]
        member_bindings = []
        for binding in filtered_bindings:
            binding.members = [
                m for m in binding.members if m.principal.endswith(domain)
            ]
            member_bindings.append(binding)
        self.bindings = member_bindings
        return self

    def filter_bindings_by_role(self, role):
        self.bindings = [b for b in self.bindings if b.role == role]
        return self

    class Binding(object):

        def __init__(self, members=[], role=''):
            self.role = role
            self.members = []
            for member_string in members:
                member = self.Member(member_string)
                self.members.append(member)

        def from_dict(self, source):
            binding = self.Binding(members=source[u'members'],
                                   role=source[u'role'])
            return binding

        def to_dict(self):
            dest = {
                u'members': [m.member for m in self.members],
                u'role': self.role
            }
            return dest

        class Member(object):
            USER_REGEX = r'(user|group|domain|serviceAccount):(.*@?\w+\.\w+)'

            def __init__(self, member_string):
                member_dict = self.split_member_email(member_string)
                self.principal_type = member_dict[u'principal_type']
                self.principal = member_dict[u'principal']
                self.member = member_dict[u'member']

            def to_dict(self):
                dest = {
                    u'principal_type': self.principal_type,
                    u'principal': self.principal,
                    u'member': self.member
                }
                return dest

            def split_member_email(self, member_string):
                try:
                    m = re.search(self.USER_REGEX, member_string)
                    return {
                        u'principal_type': m.group(1),
                        u'principal': m.group(2),
                        u'member': m.group(0),
                    }
                except Exception as e:
                    print(e)
