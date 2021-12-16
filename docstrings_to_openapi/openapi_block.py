import yaml
from yaml import Loader

from .utils import prepare_docstring


def make_openapi_route_object(view_docstring):
    """Creates the route's openapi object.

    Parameters
    ----------
    view_docstring : str

    Returns
    -------
    dict
        summary : str
        description : str
        **paths : dict

    """
    lines = prepare_docstring(view_docstring)

    (
        summary,
        description,
        block
    ) = _split_for_summary_description_openapi_doc(lines)

    openapi_ = yaml.load('\n'.join(block), Loader=Loader) or {}

    return {
        'summary': summary,
        'description': '\n'.join(description),
        **openapi_,
    }


def _split_for_summary_description_openapi_doc(lines):
    """Splites a list of docstring lines between the summary, description,
    and other properties for an API route openapi spec.

    For the openapi spec block, it should start with '````openapi' and close
    with '```'.

    Parameters
    ----------
    lines : list[str]

    Returns
    -------
    tuple
        summary : str
        description : str
        openapi : str

    """
    info = []
    openapi = []

    in_openapi = False

    for line in lines:
        if '```openapi' == line:
            in_openapi = True
            continue

        if in_openapi and '```' == line:
            in_openapi = False
            continue

        if not in_openapi:
            info.append(line)
        else:
            openapi.append(line)

    return info[0], info[1:], openapi
