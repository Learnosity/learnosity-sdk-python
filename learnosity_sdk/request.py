import datetime
import hashlib
import json

from learnosity_sdk.exceptions import ValidationException


def format_utc_time():
    "Get the current UTC time, formatted for a security timestamp"
    now = datetime.datetime.utcnow()
    return now.strftime("%Y%m%d-%H%M")


class Init(object):
    """
    This class is used to generate the necessary security and request data (in
    the correct format) to integrate with any of the Learnosity API services.
    """

    services = [
        'assess', 'author', 'data', 'events', 'items', 'questions',
        'reports'
    ]

    security_keys = [
        'consumer_key', 'domain', 'timestamp', 'user_id'
    ]

    def __init__(
            self, service, security, secret,
            request=None, action=None):
        self.service = service
        self.security = security
        self.secret = secret
        self.request = request
        self.action = action

        self.request_string = self.generate_request_string()

        self.validate()

        self.sign_request_data = True
        self.set_service_options()

        self.security['signature'] = self.generate_signature()

    def generate(self, encode=True):
        """
        Generate the data necessary to make a request to one of the Learnosity
        products/services.

        If encode is True, the result is a JSON string. Otherwise, it's a
        dictionary. If self.service == data, encode is ignored.
        """
        output = {}

        if self.service == 'questions':
            # Add the security packet to the root of output
            output.update(self.security)

            # Remove the domain key from the security packet
            del output['domain']

            # Stringify the request packet if necessary
            if self.request is not None:
                output.update(self.request_string)

        elif self.service == 'events':
            output['security'] = self.security
            output['config'] = self.request_string
        elif self.service == 'assess':
            if self.request is not None:
                output.update(self.request_string)
        elif self.service == 'data':
            # We ignore the encode param for data API
            output['security'] = json.dumps(self.security)

            if self.request is not None:
                output['request'] = self.request_string

            if self.action is not None:
                output['action'] = self.action

            return output
        else:
            output['security'] = self.security

            if self.request is not None:
                output['request'] = self.request_string

            if self.action is not None:
                output['action'] = self.action

        if encode:
            return json.dumps(output)
        else:
            return output

    def generate_request_string(self):
        if self.request is None:
            return ""
        return json.dumps(self.request)

    def generate_signature(self):

        vals = []

        # Add each valid security field.
        # The order is signifcant.
        for key in self.security_keys:
            if key in self.security:
                vals.append(self.security[key])

        # Add the secret.
        vals.append(self.secret)

        # Add the request if necessary
        if self.sign_request_data:
            vals.append(self.request_string)

        if self.action is not None:
            vals.append(self.action)

        return self.hash_list(vals)

    def validate(self):
        # Parse the security packet if the user provided it as a string
        if isinstance(self.security, str):
            self.security = json.loads(self.security)

        # Parse the request packet if the user provided it as a string
        if isinstance(self.request, str):
            self.request = json.loads(self.request)

        # Validate field lengths and types
        if len(self.service) == 0:
            raise ValidationException(
                "The \`service\` argument wasn't found or was empty")

        if len(self.secret) == 0:
            raise ValidationException(
                "The \`secret\` argument wasn't found or  was empty")

        if self.action is not None and not isinstance(self.action, str):
            raise ValidationException("The action parameter must be a string")

        # Check that service is valid
        if self.service not in self.services:
            raise ValidationException(
                "Service not valid: {}".format(self.service))

        # Check that security keys are valid
        for k in self.security.keys():
            if k not in self.security_keys:
                raise ValidationException(
                    "Invalid key found in the security packet: {}".format(k))

        # Add timestamp if missing
        if 'timestamp' not in self.security:
            self.security['timestamp'] = format_utc_time()

        # Special case for Questions API
        if self.service == 'questions' and \
                'user_id' not in self.security:
            raise ValidationException("questions API requires a user id")

    def set_service_options(self):
        if self.service == 'questions':
            self.sign_request_data = False
        elif self.service == 'assess':
            self.sign_request_data = False

            if 'questionsApiActivity' in self.request:
                questionsApi = self.request['questionsApiActivity']

                if 'domain' in self.security:
                    domain = self.security['domain']
                elif 'domain' in questionsApi:
                    domain = questionsApi['domain']
                else:
                    domain = 'assess.learnosity.com'

                self.request['questionsApiActivity'] = {
                    'consumer_key': self.security['consumer_key'],
                    'timestamp': self.security['timestamp'],
                    'user_id': self.security['user_id'],
                    'signature': self.hash_list({
                        'consumer_key': self.security['consumer_key'],
                        'domain': domain,
                        'timestamp': self.security['timestamp'],
                        'user_id': self.security['user_id'],
                        'secret': self.secret
                    }.values())
                }

                del questionsApi['consumer_key']
                del questionsApi['domain']
                del questionsApi['timestamp']
                del questionsApi['user_id']
                del questionsApi['signature']

                self.request['questionsApiActivity'].update(questionsApi)

        elif self.service == 'items' or self.service == 'reports':
            if 'user_id' not in self.security and \
                    'user_id' in self.request:
                self.security['user_id'] = self.request['user_id']

        elif self.service == 'events':
            self.sign_request_data = False
            hashed_users = {}
            for user in self.request.get('users', []):
                concat = "{}{}".format(user, self.security['consumer_key'])
                hashed_users[user] = hashlib.sha256(concat)

            if len(hashed_users) > 0:
                self.request['users'] = hashed_users

    def hash_list(self, l):
        "Hash a list by concatenating values with an underscore"
        return hashlib.sha256("_".join(l).encode('utf-8')).hexdigest()
