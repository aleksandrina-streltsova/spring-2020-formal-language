import pytest
import rdflib as rdf
import networkx as nx


def test_undirected_graph():
    rdf_graph = rdf.Graph().parse('tests/acquaintance-graph.nt', format='nt')
    ns = rdf.Namespace("http://example.org/people/")
    graph = nx.Graph()
    graph.add_edges_from(list(rdf_graph.subject_objects(rdf.namespace.FOAF.knows)))
    assert (ns.Bob in graph.nodes())
    assert (ns.Tom not in graph.nodes)
    assert (nx.has_path(graph, ns.Bob, ns.Mike))
    assert (not nx.has_path(graph, ns.Jane, ns.Bob))
    assert (not nx.is_connected(graph))


def test_directed_graph():
    rdf_graph = rdf.Graph().parse('tests/acquaintance-graph.nt', format='nt')
    ns = rdf.Namespace("http://example.org/people/")
    graph = nx.DiGraph()
    graph.add_edges_from(list(rdf_graph.subject_objects(rdf.namespace.FOAF.knows)))
    assert (nx.has_path(graph, ns.Bob, ns.Mike))
    assert (not nx.has_path(graph, ns.Mike, ns.Bob))


if __name__ == '__main__':
    pytest.main()
