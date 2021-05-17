# LTI 1.1
# Defined from https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide
# We define the user_id as required even though it is defined as recommended as it used as
# a fallback id for nbgrader's lms_user_id column.
LTI11_LAUNCH_PARAMS_REQUIRED = [
    "lti_message_type",
    "lti_version",
    "resource_link_id",
    "user_id",
]

LTI11_LAUNCH_PARAMS_RECOMMENDED = [
    "resource_link_title",
    "roles",
    "lis_person_name_given",
    "lis_person_name_family",
    "lis_person_name_full",
    "lis_person_contact_email_primary",
    "context_id",
    "context_title",
    "context_label",
    "launch_presentation_locale",
    "launch_presentation_document_target",
    "launch_presentation_width",
    "launch_presentation_height",
    "launch_presentation_return_url",
    "tool_consumer_info_product_family_code",
    "tool_consumer_info_version",
    "tool_consumer_instance_guid",
    "tool_consumer_instance_name",
    "tool_consumer_instance_contact_email",
]

LTI11_LAUNCH_PARAMS_OTIONAL = [
    "resource_link_description",
    "user_image",
    "role_scope_mentor",
    "context_type",
    "launch_presentation_css_url",
    "tool_consumer_instance_description",
    "tool_consumer_instance_url",
]

LTI11_LIS_OPTION = [
    "lis_outcome_service_url",
    "lis_result_sourcedid",
    "lis_person_sourcedid",
    "lis_course_offering_sourcedid",
    "lis_course_section_sourcedid",
]

# https://www.imsglobal.org/specs/ltiv1p1/implementation-guide
# Section 4.2
LTI11_OAUTH_ARGS = [
    "oauth_consumer_key",
    "oauth_signature_method",
    "oauth_timestamp",
    "oauth_nonce",
    "oauth_callback",
    "oauth_version",
    "oauth_signature",
]

LTI11_LAUNCH_PARAMS_REQUIRED = LTI11_LAUNCH_PARAMS_REQUIRED + LTI11_OAUTH_ARGS

LTI11_LAUNCH_PARAMS_ALL = (
    LTI11_LAUNCH_PARAMS_REQUIRED
    + LTI11_LAUNCH_PARAMS_RECOMMENDED
    + LTI11_LAUNCH_PARAMS_OTIONAL
)
