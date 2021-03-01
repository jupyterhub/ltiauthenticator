import json
import pytest

from tornado.web import RequestHandler

from unittest.mock import patch

from ltiauthenticator.lti13.handlers import LTI13ConfigHandler


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_calls_write_method(mock_write, lti13_config_environ, make_mock_request_handler):
    """
    Is the write method used in get method?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    assert mock_write.called


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_calls_write_method_with_a_json(mock_write, lti13_config_environ, make_mock_request_handler):
    """
    Does the write base method is invoked with a string?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    # call_args is a list
    write_args = mock_write.call_args[0]
    # write_args == tuple
    json_arg = write_args[0]
    assert type(json_arg) == str
    assert json.loads(json_arg)


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_writes_a_json_with_required_keys(
    mock_write, lti13_config_environ, make_mock_request_handler
):
    """
    Does the get method write a json (jwks) with essential fields?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    keys_at_0_level_expected = [
        'title',
        'target_link_uri',
        'scopes',
        'public_jwk_url',
        'public_jwk',
        'oidc_initiation_url',
        'extensions',
        'custom_fields',
    ]
    # call_args is a list
    # so we're only extracting the json arg
    json_arg = mock_write.call_args[0][0]
    for required_key in keys_at_0_level_expected:
        assert required_key in json_arg


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_writes_our_company_name_in_the_title_field(
    mock_write, lti13_config_environ, make_mock_request_handler
):
    """
    Does the get method write 'LTIAuthenticator' value as the title in the json?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    # call_args is a list
    # so we're only extracting the json arg
    json_arg = mock_write.call_args[0][0]
    title = json.loads(json_arg)['title']
    assert title == 'LTIAuthenticator'


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_writes_email_field_within_custom_fields(
    mock_write, lti13_config_environ, make_mock_request_handler
):
    """
    Does the get method write 'email' field as a custom_fields?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    # call_args is a list
    # so we're only extracting the json arg
    json_arg = mock_write.call_args[0][0]
    custom_fields = json.loads(json_arg)['custom_fields']
    assert 'email' in custom_fields
    assert '$Person.email.primary' == custom_fields['email']


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_writes_email_custom_field_within_each_course_navigation_placement(
    mock_write, lti13_config_environ, make_mock_request_handler
):
    """
    Does the get method write 'email' field in custom_fields within each course_navigation placement setting?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    # call_args is a list
    # so we're only extracting the json arg
    json_arg = mock_write.call_args[0][0]
    extensions = json.loads(json_arg)['extensions']
    course_navigation_placement = None
    for ext in extensions:
        # find the settings field in each extension to ensure a course_navigation placement was used
        if 'settings' in ext and 'placements' in ext['settings']:
            course_navigation_placement = [
                placement
                for placement in ext['settings']['placements']
                if placement['placement'] == 'course_navigation'
            ]

            assert course_navigation_placement
            placement_custom_fields = course_navigation_placement[0]['custom_fields']
            assert placement_custom_fields
            assert placement_custom_fields['email']
            assert placement_custom_fields['email'] == '$Person.email.primary'


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_writes_lms_user_id_field_within_custom_fields(
    mock_write, lti13_config_environ, make_mock_request_handler
):
    """
    Does the get method write 'lms_user_id' field within custom_fields and use the $User.id property?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    # call_args is a list
    # so we're only extracting the json arg
    json_arg = mock_write.call_args[0][0]
    custom_fields = json.loads(json_arg)['custom_fields']
    assert 'lms_user_id' in custom_fields
    assert '$User.id' == custom_fields['lms_user_id']


@pytest.mark.asyncio
@patch('tornado.web.RequestHandler.write')
async def test_get_method_writes_lms_user_id_custom_field_within_each_course_navigation_placement(
    mock_write, lti13_config_environ, make_mock_request_handler
):
    """
    Does the get method write 'lms_user_id' field in custom_fields within each course_navigation placement setting?
    """
    handler = make_mock_request_handler(RequestHandler)
    config_handler = LTI13ConfigHandler(handler.application, handler.request)
    # this method writes the output to internal buffer
    await config_handler.get()
    # call_args is a list
    # so we're only extracting the json arg
    json_arg = mock_write.call_args[0][0]
    extensions = json.loads(json_arg)['extensions']
    course_navigation_placement = None
    for ext in extensions:
        # find the settings field in each extension to ensure a course_navigation placement was used
        if 'settings' in ext and 'placements' in ext['settings']:
            course_navigation_placement = [
                placement
                for placement in ext['settings']['placements']
                if placement['placement'] == 'course_navigation'
            ]

            assert course_navigation_placement
            placement_custom_fields = course_navigation_placement[0]['custom_fields']
            assert placement_custom_fields
            assert placement_custom_fields['lms_user_id']
            assert placement_custom_fields['lms_user_id'] == '$User.id'
