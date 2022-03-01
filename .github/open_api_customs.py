import json

OPEN_API_FILE = open(".github/openapi.json")
OPEN_API_SCHEMA = json.load(OPEN_API_FILE)
OPEN_API_FILE.close()
SECTIONS_ORDER = [
    "keywords",
    "message_requests",
    "sent_messages",
    "subscribers",
    "webhooks",
]
PATHS_ORDER = [
    "/api/v2/me",
    "/api/v2/keywords",
    "/api/v2/keywords/{keyword_id}",
    "/api/v2/message_requests/{external_id}",
    "/api/v2/message_requests",
    "/api/v2/sent_messages/{external_id}",
    "/api/v2/subscribers",
    "/api/v2/subscribers/{external_id}",
    "/api/v2/subscribers/pending",
    "/api/v2/subscribers/pending/{external_id}",
    "/api/v2/webhooks",
    "/api/v2/webhooks/{webhook_id}",
    "/api/v2/webhooks/token",
    "/api/v2/webhooks/test",
]
OPEN_API_ENDPOINTS_NAMES = {
    "Fetch Keywords List": "Get Keywords",
    "Fetch Single Keyword": "Get Keyword",
    "Fetch Subscribers List": "Get Subscribers",
    "Fetch Subscriber": "Get Subscriber",
    "Put Subscriber": "Update Subscriber",
    "Patch Subscriber": "Update Subscriber",
    "Fetch Pending Subscribers List": "Get Pending Subscribers",
    "Fetch Pending Subscriber": "Get Pending Subscriber",
    "Fetch Message Request": "Get Message Request",
    "Create Message Request": "Send Message",
    "Fetch Sent Message": "Get Sent Message",
    "Fetch Webhook Subscription": "Get Webhook Subscription",
    "Webhook Signing Token": "Get Webhook Signing Token",
    "Create Custom Subscriber Event": "Create Custom Event",
    "Get Custom Subscriber Event": "Get Subscriber Event",
}
OPEN_API_SECTION_NAMES = {
    "Custom Subscriber Events": "Custom Events",
}
PATH_PARAMS_NAMES = {"keyword_id": "id", "external_id": "id", "webhook_id": "id"}
COMPONENT_SCHEMAS_CHANGES = {
    "CreateSingleSubscriber": {"properties": {"properties": {"type": "object"}}},
    "UpdateSingleSubscriber": {"properties": {"properties": {"type": "object"}}},
}

print(
    "Performing redaction and order changes on the OpenAPI schema before official doc synch..."
)
OPEN_API_SCHEMA["info"]["title"] = "Postscript API"
reordered_sections = {}
reordered_paths = {}

# Reordering sections
reordered_sections["/api/v2/me"] = OPEN_API_SCHEMA["paths"]["/api/v2/me"]
for section in SECTIONS_ORDER:
    for path in OPEN_API_SCHEMA["paths"]:
        if section in path:
            reordered_sections[path] = OPEN_API_SCHEMA["paths"][path]
OPEN_API_SCHEMA["paths"] = reordered_sections

# Reordering paths
for new_path in PATHS_ORDER:
    for path in OPEN_API_SCHEMA["paths"]:
        if new_path == path:
            reordered_paths[path] = OPEN_API_SCHEMA["paths"][path]
OPEN_API_SCHEMA["paths"] = reordered_paths

open_api_paths = dict(OPEN_API_SCHEMA["paths"])
for path in open_api_paths:
    path_param_name = ""
    adjusted_path_param = ""

    for method in open_api_paths[path]:
        if method != "parameters":
            spec = open_api_paths[path][method]

            # Overwriting the endpoint names on 'summary' field for each
            if spec["summary"] in OPEN_API_ENDPOINTS_NAMES:
                original_name = spec["summary"]
                parsed_name = OPEN_API_ENDPOINTS_NAMES[spec["summary"]]
                original_camel_case = spec["summary"].replace(" ", "")
                OPEN_API_SCHEMA["paths"][path][method]["summary"] = parsed_name
                parsed_camel_case = parsed_name.replace(" ", "")
                for status_code in spec["responses"]:
                    if (
                        original_camel_case
                        in spec["responses"][status_code]["description"]
                    ):
                        OPEN_API_SCHEMA["paths"][path][method]["responses"][
                            status_code
                        ]["description"] = spec["responses"][status_code][
                            "description"
                        ].replace(
                            original_camel_case, parsed_camel_case
                        )

            # Overwriting the endpoint sections on 'tags' field for each
            if spec["tags"][0] in OPEN_API_SECTION_NAMES:
                adjusted_section = OPEN_API_SECTION_NAMES[spec["tags"][0]]
                spec["tags"][0] = adjusted_section

            # Overwriting endpoint's path parameter names
            if (
                len(spec["parameters"]) != 0
                and spec["parameters"][0]["in"] == "path"
                and spec["parameters"][0]["name"] in PATH_PARAMS_NAMES
            ):
                path_param_name = spec["parameters"][0]["name"]
                adjusted_path_param = PATH_PARAMS_NAMES[path_param_name]
                spec["parameters"][0]["name"] = adjusted_path_param

    # Once path parameter names are overwritten, they MUST be overwritten in the path as well for OpenAPI compliance
    adjusted_path = path.replace(f"{{{path_param_name}}}", f"{{{adjusted_path_param}}}")
    OPEN_API_SCHEMA["paths"][adjusted_path] = OPEN_API_SCHEMA["paths"].pop(path)

# Component Schema Changes
for schema in COMPONENT_SCHEMAS_CHANGES:
    OPEN_API_SCHEMA["components"]["schemas"][schema]["properties"]["properties"][
        "type"
    ] = COMPONENT_SCHEMAS_CHANGES[schema]["properties"]["properties"]["type"]
    OPEN_API_SCHEMA["components"]["schemas"][schema]["properties"]["properties"].pop(
        "format"
    )
    OPEN_API_SCHEMA["components"]["schemas"][schema]["properties"]["properties"][
        "maxProperties"
    ] = 20

with open(".github/openapi.json", "w") as updated_open_api:
    json.dump(OPEN_API_SCHEMA, updated_open_api)
