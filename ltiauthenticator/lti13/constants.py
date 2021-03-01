# LTI 1.3

# Initial authentication request arguments
# https://www.imsglobal.org/spec/security/v1p0/#step-1-third-party-initiated-login
LTI13_LOGIN_REQUEST_ARGS = [
    "iss",
    "login_hint",
    "target_link_uri",
]

# Initial authentication request arguments
# https://www.imsglobal.org/spec/security/v1p0/#step-2-authentication-request
LTI13_AUTH_REQUEST_ARGS = [
    "client_id",
    "login_hint",
    "lti_message_hint",
    "nonce",
    "prompt",
    "redirect_uri",
    "response_mode",
    "response_type",
    "scope",
    "state",
]

# Required message claims
# http://www.imsglobal.org/spec/lti/v1p3/#required-message-claims
LTI13_GENERAL_REQUIRED_CLAIMS = {
    "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
    "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "",
    "https://purl.imsglobal.org/spec/lti/claim/target_link_uri": "",
    "https://purl.imsglobal.org/spec/lti/claim/roles": "",
}

# Required claims with LtiResourceLinkRequest login flows
LTI13_RESOURCE_LINK_REQUIRED_CLAIMS = {
    "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
    "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
        "id": "",
    },  # noqa: E231
    **LTI13_GENERAL_REQUIRED_CLAIMS,
}

# Required claims with LtiDeepLinkingRequest login flows
LTI13_DEEP_LINKING_REQUIRED_CLAIMS = {
    "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiDeepLinkingRequest",
    **LTI13_GENERAL_REQUIRED_CLAIMS,
}

# Optional message claims
# We don't need the role_scope_mentor claim and some platforms don't send this claim by default.
# http://www.imsglobal.org/spec/lti/v1p3/#optional-message-claims
LTI13_GENERAL_OPTIONAL_CLAIMS = {
    "https://purl.imsglobal.org/spec/lti/claim/context": {
        "id": "",
        "label": "",
        "title": "",
        "type": [
            "http://purl.imsglobal.org/vocab/lis/v2/course#CourseTemplate",
            "http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering",
            "http://purl.imsglobal.org/vocab/lis/v2/course#CourseSection",
            "http://purl.imsglobal.org/vocab/lis/v2/course#Group",
        ],
    },
    # user identity claims. sub (subject) is added to optional list to support anonymous
    # launches.
    "aud": "",
    "azp": "",
    "exp": None,
    "iat": None,
    "iss": "",
    "nonce": "",
    "sub": "",
    "https://purl.imsglobal.org/spec/lti/claim/tool_platform": {
        "guid": "",
        "name": "",
        "version": "",
        "product_family_code": "",
        "validation_context": None,
        "errors": {"errors": {}},
    },
    "https://purl.imsglobal.org/spec/lti/claim/launch_presentation": {
        # one of frame, iframe, window
        "document_target": "",
        "height": "",
        "width": "",
        "return_url": "",
        "locale": "",
    },
}

# Optional resource link request claims
LTI13_RESOURCE_LINK_OPTIONAL_CLAIMS = {
    **LTI13_GENERAL_OPTIONAL_CLAIMS,
    "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
        "description": "",
        "title": "",
    },  # noqa: E231
}

# Required claims for deep linking request claims
LTI13_DEEP_LINKING_REQUIRED_CLAIMS = {
    **LTI13_DEEP_LINKING_REQUIRED_CLAIMS,
    **LTI13_GENERAL_OPTIONAL_CLAIMS,
}

# Optional learning information system (LIS) claims
LTI13_LIS_CLAIMS = {
    "https://purl.imsglobal.org/spec/lti/claim/lis": {
        "course_offering_sourcedid": "",
        "course_section_sourcedid": "",
        "outcome_service_url": "",
        "person_sourcedid": "",
        "result_sourcedid": "",
    },
}

# Required claims for ResourceLinkRequest
# For this setup to work properly, some optional claims are required.
LTI13_RESOURCE_LINK_REQUIRED_CLAIMS = {
    **LTI13_RESOURCE_LINK_REQUIRED_CLAIMS,
    **LTI13_RESOURCE_LINK_OPTIONAL_CLAIMS,
}

# Required and optional resource link claims
LTI13_RESOURCE_LINKS = {
    **LTI13_RESOURCE_LINK_REQUIRED_CLAIMS[
        "https://purl.imsglobal.org/spec/lti/claim/resource_link"
    ],
    **LTI13_RESOURCE_LINK_OPTIONAL_CLAIMS[
        "https://purl.imsglobal.org/spec/lti/claim/resource_link"
    ],
}

# Updates required claims with optional claims
LTI13_RESOURCE_LINK_REQUIRED_CLAIMS[
    "https://purl.imsglobal.org/spec/lti/claim/resource_link"
].update(LTI13_RESOURCE_LINKS)

# Required claims for DeepLinkingRequest
LTI13_DEEP_LINKING_REQUIRED_CLAIMS = {
    **LTI13_DEEP_LINKING_REQUIRED_CLAIMS,
    **LTI13_GENERAL_OPTIONAL_CLAIMS,
}

LTI13_ROLE_VOCABULARIES = {
    "SYSTEM_ROLES": {
        "CORE": {
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#None",
        },
        "NON_CORE": {
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#User",
        },
    },
    "INSTITUTION_ROLES": {
        "CORE": {
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#None",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
        },
        "NON_CORE": {
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent",
        },
    },
    "CONTEXT_ROLES": {
        "CORE": {
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor",
        },
        "NON_CORE": {
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Member",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer",
        },
        "CONTEXT_SUB_ROLES": {
            # administrator role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#Developer",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#ExternalDeveloper",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#ExternalSupport",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#ExternalSystemAdministrator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#Support",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#SystemAdministrator",
            # content developer role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#ContentDeveloper",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#ContentExpert",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#ExternalContentExpert",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#Librarian",
            # instructor role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#ExternalInstructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#Grader",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#GuestInstructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#Lecturer",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#PrimaryInstructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#SecondaryInstructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistant",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantGroup",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantOffering",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantSection",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantSectionAssociation",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantTemplate",
            # Learner role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#ExternalLearner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#GuestLearner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#NonCreditLearner",
            # Manager role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#AreaManager",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#CourseCoordinator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#ExternalObserver",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#Manager",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#Observer",
            # Member role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Member#Member",
            # Mentor role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Mentor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Advisor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Auditor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalAdvisor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalAuditor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalLearningFacilitator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalMentor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalReviewer",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalTutor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#LearningFacilitator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Reviewer",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Tutor",
            # Officer role
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Chair",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Communications",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Secretary",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Treasurer",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Vice-Chair",
        },
    },
}

LTI13_ROLES = {
    "STAFF_ROLES": {
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#None",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager",
    },
    "STUDENT_ROLES": {
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#ExternalLearner",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Instructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#GuestLearner",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#NonCreditLearner",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent",
    },
    "INSTRUCTOR_ROLES": {
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#Grader",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantOffering",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantSectionAssociation",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#PrimaryInstructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#GuestInstructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantSection",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#SecondaryInstructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#Lecturer",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Instructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantGroup",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistant",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#ExternalInstructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantTemplate",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
    },
}

# the list of roles that recognize a user as a Student
DEFAULT_ROLE_NAMES_FOR_STUDENT = ["student", "learner"]
# the list of roles that recognize a user as an Instructor
DEFAULT_ROLE_NAMES_FOR_INSTRUCTOR = [
    "instructor",
    "urn:lti:role:ims/lis/teachingassistant",
]
