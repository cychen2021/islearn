import copy
import string
import xml.etree.ElementTree as ET
from html import escape
from typing import Optional, List

from fuzzingbook.Grammars import srange

from isla.isla import parse_isla, DerivationTree
from isla.isla_predicates import IN_TREE_PREDICATE, SAME_POSITION_PREDICATE

XML_GRAMMAR = {
    "<start>": ["<xml-tree>"],
    "<xml-tree>": [
        "<xml-open-tag><inner-xml-tree><xml-close-tag>",
        "<xml-openclose-tag>",
    ],
    "<inner-xml-tree>": [
        "<text>",
        "<xml-tree>",
        "<inner-xml-tree><inner-xml-tree>"
    ],
    "<xml-open-tag>": ["<<id>>", "<<id> <xml-attribute>>"],
    "<xml-openclose-tag>": ["<<id>/>", "<<id> <xml-attribute>/>"],
    "<xml-close-tag>": ["</<id>>"],
    "<xml-attribute>": ["<id>=\"<text>\"", "<xml-attribute> <xml-attribute>"],

    "<id>": [
        "<id-start-char>",
        "<id-start-char><id-chars>",
    ],
    "<id-start-char>": srange("_" + string.ascii_letters),
    "<id-chars>": ["<id-char>", "<id-char><id-chars>"],
    "<id-char>": ["<id-start-char>"] + srange("-." + string.digits),
    "<text>": ["<text-char><text>", "<text-char>"],
    "<text-char>": [
        escape(c, {'"': "&quot;"})
        for c in srange(string.ascii_letters + string.digits + "\"'. \t/?-,=:+")],
}

XML_GRAMMAR_WITH_NAMESPACE_PREFIXES = copy.deepcopy(XML_GRAMMAR)
XML_GRAMMAR_WITH_NAMESPACE_PREFIXES.update({
    "<id>": [
        "<id-no-prefix>",
        "<id-with-prefix>"
    ],
    "<id-no-prefix>": [
        "<id-start-char>",
        "<id-start-char><id-chars>",
    ],
    "<id-with-prefix>": ["<id-no-prefix>:<id-no-prefix>"]
})


def validate_xml(inp: DerivationTree, out: Optional[List[str]] = None) -> bool:
    try:
        ET.fromstring(str(inp))
        return True
    except Exception as err:
        if out is not None:
            out.append(str(err))
        return False


xml_wellformedness_constraint = """
const start: <start>;

vars {
    tree: <xml-tree>;
    opid, clid: <id>;
}

constraint {
    forall tree="<{opid}[ <xml-attribute>]><inner-xml-tree></{clid}>" in start:
        (= opid clid)
}
"""

XML_WELLFORMEDNESS_CONSTRAINT = parse_isla(xml_wellformedness_constraint)

xml_attribute_namespace_constraint = """
const start: <start>;

vars {
    prefix_id: <id-with-prefix>;
    prefix_use, prefix_def: <id-no-prefix>;
    outer_tag: <xml-tree>;
    attribute, cont_attribute, def_attribute: <xml-attribute>;
    contained_tree: <inner-xml-tree>;
}

constraint {
    forall attribute in start:
        forall prefix_id="{prefix_use}:<id-no-prefix>" in attribute:
            ((= prefix_use "xmlns") or
                exists outer_tag="<<id> {cont_attribute}>{contained_tree}</<id>>" in start:
                    (inside(attribute, contained_tree) and 
                     exists def_attribute="xmlns:{prefix_def}=\\\"<text>\\\"" in cont_attribute:
                         (= prefix_use prefix_def)))
}
"""

XML_ATTRIBUTE_NAMESPACE_CONSTRAINT = parse_isla(
    xml_attribute_namespace_constraint, structural_predicates={IN_TREE_PREDICATE})

xml_tag_namespace_constraint = """
const start: <start>;

vars {
    prefix_id: <id-with-prefix>;
    prefix_use, prefix_def: <id-no-prefix>;
    xml_tree, outer_tag: <xml-tree>;
    cont_attribute, def_attribute: <xml-attribute>;
    contained_tree: <inner-xml-tree>;
}

constraint {
    forall xml_tree="<{prefix_use}:<id-no-prefix>[ <xml-attribute>][/]>[<inner-xml-tree><xml-close-tag>]" in start:
        exists outer_tag="<<id> {cont_attribute}>{contained_tree}</<id>>" in start:
            (inside(xml_tree, contained_tree) and 
             exists def_attribute="xmlns:{prefix_def}=\\\"<text>\\\"" in cont_attribute:
                 (= prefix_use prefix_def))
}
"""

XML_TAG_NAMESPACE_CONSTRAINT = parse_isla(xml_tag_namespace_constraint, structural_predicates={IN_TREE_PREDICATE})

XML_NAMESPACE_CONSTRAINT = XML_TAG_NAMESPACE_CONSTRAINT & XML_ATTRIBUTE_NAMESPACE_CONSTRAINT

xml_no_attr_redef_constraint = """
const start: <start>;

vars {
  attr_outer, attr_inner_1, attr_inner_2: <xml-attribute>;
  id_1, id_2: <id>;
}

constraint {
  forall attr_outer in start:
    forall attr_inner_1="{id_1}=\\\"<text>\\\"" in attr_outer:
      forall attr_inner_2="{id_2}=\\\"<text>\\\"" in attr_outer: 
        (not same_position(attr_inner_1, attr_inner_2) implies
         not (= id_1 id_2))
}
"""

XML_NO_ATTR_REDEF_CONSTRAINT = parse_isla(
    xml_no_attr_redef_constraint,
    structural_predicates={
        IN_TREE_PREDICATE,
        SAME_POSITION_PREDICATE})
