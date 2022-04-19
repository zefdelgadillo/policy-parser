from googleapiclient import discovery, errors
from oauth2client.client import GoogleCredentials, ApplicationDefaultCredentialsError
import logging


class Role:

    def __init__(self, roles, permission=''):
        self.roles = set(roles)
        self.permission = permission
        try:
            credentials = GoogleCredentials.get_application_default()
            self.service = discovery.build('iam',
                                           'v1',
                                           credentials=credentials)
        except ApplicationDefaultCredentialsError:
            raise (AuthenticationError(
                'Not authenticated to Google Cloud. Try running `gcloud auth application-default login` \n\nSee https://developers.google.com/accounts/docs/application-default-credentials for more information.'
            ))

    def permissions(self, role):
        try:
            request = self.service.roles().get(name=role)
            response = request.execute()
            return response[u'includedPermissions']
        except errors.HttpError as e:
            logging.warn(e.error_details)
            return

    def matching_roles(self):
        role_matches = self.match_roles_to_permissions()
        roles = [role for role, match in role_matches if match == True]
        logging.info('%s found in %s', self.permission, roles)
        return roles

    def get_permissions_from_roles(self):
        role_dict = {}
        for role in self.roles:
            permissions = self.permissions(role)
            if isinstance(permissions, list):
                role_dict[role] = permissions
        return (role_dict)

    def match_roles_to_permissions(self):
        role_permissions = self.get_permissions_from_roles()
        role_matches = []
        for (role, permissions) in role_permissions.items():
            role_permission_match = (role, (self.permission in permissions))
            role_matches.append(role_permission_match)
        return role_matches


class AuthenticationError(Exception):
    pass
