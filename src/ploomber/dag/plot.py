import json
import sys
from importlib.util import find_spec
from pathlib import Path
from IPython.display import IFrame

import jinja2

try:
    import importlib.resources as importlib_resources
except ImportError:  # pragma: no cover
    # backported
    import importlib_resources

from ploomber import resources


def check_pygraphviz_installed():
    return find_spec("pygraphviz") is not None


def check_if_windows_python_3_10():
    return 'win' in sys.platform and sys.version_info >= (3, 10)


def choose_backend(backend):
    """Determine which backend to use for plotting
       Temporarily disable pygraphviz for Python 3.10 on Windows
    """
    if ((not check_pygraphviz_installed() and backend is None)
            or (backend == 'd3') or (check_if_windows_python_3_10())):
        return 'd3'

    return 'pygraphviz'


def json_dag_parser(graph: dict):
    """Format dag dict so d3 can understand it
    """
    nodes = {}

    for task in graph["nodes"]:
        nodes[task["id"]] = task

    # change name label to products for now
    for node in nodes:
        nodes[node]["products"] = (nodes[node]["label"].replace("\n",
                                                                "").split(","))

    for link in graph["links"]:
        node_links = nodes[link["target"]].get("parentIds", [])
        node_links.append(link["source"])
        nodes[link["target"]]["parentIds"] = node_links

    return json.dumps(list(nodes.values()))


def with_d3(graph, output):
    """Generates D3 Dag html output and return output file name
    """
    template = jinja2.Template(
        importlib_resources.read_text(resources, 'dag_template.html'))

    rendered = template.render(json_data=json_dag_parser(graph=graph))
    Path(output).write_text(rendered)


def embedded_html(path):
    return IFrame(src=path)
