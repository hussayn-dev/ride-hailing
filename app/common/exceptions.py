from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class UnprocessableException(APIException):
    status_code = 422
    default_detail = 'Request cannot be process, missing important configurations'
    default_code = 'unprocessable'


class NotFoundException(APIException):
    status_code = 404
    default_detail = 'Requested entity does not exist'
    default_code = 'not_found'


class PermissionDeniedException(APIException):
    status_code = 403
    default_detail = "You don't have the permission to access this resource "
    default_code = 'permission_denied'


class BadRequestException(APIException):
    status_code = 400
    default_detail = 'Bad Request '
    default_code = 'bad_request'

class AuthenticationRequestException(APIException):
    status_code = 401
    default_detail = 'Authentication credentials were not provided.'
    default_code = 'not_authenticated'