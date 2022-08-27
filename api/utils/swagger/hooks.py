import logging
from functools import reduce
from typing import Sequence, Set

import yaml
from django.conf import settings

from api.openapi.x_logo_info import X_LOGO_INFO

logger = logging.getLogger(__name__)


def remove_password_reset_paths(endpoints: Sequence):
    def _valid_endpoint(ep):
        path = ep[0]
        return '/auth' not in path
    return list(filter(lambda endpoint: _valid_endpoint(endpoint), endpoints))


def fix_TokenAuthentication_docs(result, **kwargs):
    result['components']['securitySchemes']['tokenAuth'] = {
        **result['components']['securitySchemes']['tokenAuth'],
        'description': (
            'Token-based authentication uses the `Authorization` header and a value that follows '
            'the format of `Token <some token>`, where `<some token>` is fetched from the API using '
            "a user's credentials.\n\nThe token can be generated from making a `POST` request to "
            "`/auth/token/login/` with a JSON payload of the user's `email` and `password`."
        ),
    }
    result_dump = yaml.dump(result).replace('tokenAuth', 'Token_Authentication')
    return yaml.load(result_dump, Loader=yaml.Loader)


def populate_rich_openapi_tags(result, **kwargs):
    """This organizes the routes and sections into nice categories
    """
    tag_docs_path = settings.BASE_DIR / 'openapi/tags.yaml'
    with open(tag_docs_path, 'r') as f:
        tag_docs = yaml.safe_load(f.read())

    if not tag_docs:
        return result

    tags: Set[str] = set()
    for path_operations in result['paths'].values():
        for operation in path_operations.values():
            tags.update(operation['tags'])

    # Map all tags to objects, add description where needed
    tags_data = []
    for tag in tags:
        tag_data = tag_docs.get(tag, {})
        if not tag_data:
            logger.warning('at=populate_openapi_tags tag="%s" error="does not have any documentation included"', tag)
            tags_data.append({'name': tag, 'x-displayName': tag.title()})
        else:
            tags_data.append({**tag_data, 'name': tag})

    tags = sorted(tags_data, key=lambda t: t.get('x-displayName', t['name']))
    result['tags'] = tags

    if 'tagGroups' in tag_docs:
        groups = tag_docs['tagGroups']
        result['x-tagGroups'] = groups

        all_grouped_tags = set(reduce(lambda tags, group: [*tags, *group.get('tags', [])], groups, []))  # strings
        missing_tags = list(filter(lambda t: t['name'] not in all_grouped_tags, tags))  # rich tag dicts
        uncategorized = {
            'name': 'Uncategorized',
            'tags': list(map(lambda t: t['name'], missing_tags)),
        }
        result['x-tagGroups'].append(uncategorized)

    return result


def add_x_logo_info(result, **kwargs):
    """Show a nice logo in the top left of the documentation
    """
    result['info']['x-logo'] = X_LOGO_INFO
    return result
