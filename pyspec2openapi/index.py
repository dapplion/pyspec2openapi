import re
import copy
import requests
from deepmerge import always_merger  # type: ignore
from typing import Dict, List, Tuple
import itertools
import sys


spec_base_url = 'https://raw.githubusercontent.com/ethereum/consensus-specs'

primitive_types = {
    'boolean': {'type': 'boolean', 'example': False},
    'uint8': {'type': 'integer', 'example': 1},
    'uint64': {'type': 'string', 'example': '1'},
    'uint256': {'type': 'string', 'example': '1'},
    'Bitlist': {'type': 'string', 'format': 'hex', 'example': '0x01', 'pattern': '^0x[a-fA-F0-9]+$'},
    'Bitvector': {'type': 'string', 'format': 'hex', 'example': '0x01', 'pattern': '^0x[a-fA-F0-9]+$'},
    'ByteList': {'type': 'string', 'format': 'hex', 'example': '0x01', 'pattern': '^0x[a-fA-F0-9]+$'},
    'ByteVector': {'type': 'string', 'format': 'hex', 'example': '0x01', 'pattern': '^0x[a-fA-F0-9]+$'},
}


def parse_specs(config: Dict) -> Dict:
    sources = config['sources']

    out = {
        'primitive': primitive_types.copy()
    }
    # https://raw.githubusercontent.com/ethereum/consensus-specs/v1.4.0-beta.5/specs/phase0/beacon-chain.md
    for fork in sources:
        out[fork] = {}
        config.setdefault('mutations', {})[fork] = []
        config.setdefault('dependants', {})
        config.setdefault('class_code', {})

        for source in sources[fork]:
            doc = fetch_source(source, fork, config)
            parse_doc(doc, fork, config, out)

        for mutated_class in config['mutations'][fork]:
            for dependant_class in config['dependants'].get(mutated_class, set()):
                if dependant_class not in out[fork]:
                    print(f"Adding spec for {fork}.{dependant_class}", file=sys.stderr)
                    parse_container_code_block(
                        config['class_code'][dependant_class], fork, config, out
                    )

        if fork in config.get('generate_blinded_types', []):
            generate_blinded_types(fork, config, out)

    if 'override_schema' in config:
        # result = always_merger.merge(base, next)
        out = always_merger.merge(out, config['override_schema'])

    return out


def fetch_source(source: Dict, fork: str, config: Dict) -> str:
    spec_filename = source.get('spec')
    if spec_filename is not None:
        version = config['version']
        url = f"{spec_base_url}/{version}/specs/{fork}/{spec_filename}"
        print(f"fetching {url}", file=sys.stderr)
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    
    local_filepath = source.get('file')
    if local_filepath is not None:
        print(f"reading {local_filepath}")
        with open(local_filepath, 'r') as file:
            return file.read()

    raise Exception("sources item must declare 'spec' or 'file'")


def generate_blinded_types(fork: str, config: Dict, out: Dict):
    blinded_beacon_block_body = copy.deepcopy(out[fork]['BeaconBlockBody'])
    blinded_beacon_block = copy.deepcopy(out[fork]['BeaconBlock'])
    signed_blinded_beacon_block = copy.deepcopy(out[fork]['SignedBeaconBlock'])

    del blinded_beacon_block_body['properties']['execution_payload']
    blinded_beacon_block_body['properties']['execution_payload_header'] = \
        get_type_schema(fork, "ExecutionPayloadHeader", "", config, out)

    out[fork]['BlindedBeaconBlockBody'] = blinded_beacon_block_body
    blinded_beacon_block['properties']['body'] = \
        get_type_schema(fork, "BlindedBeaconBlockBody", "", config, out)

    out[fork]['BlindedBeaconBlock'] = blinded_beacon_block
    signed_blinded_beacon_block['properties']['message'] = \
        get_type_schema(fork, "BlindedBeaconBlock", "", config, out)

    out[fork]['SignedBlindedBeaconBlock'] = signed_blinded_beacon_block


def parse_doc(doc: str, fork: str, config: Dict, out: Dict):
    for row in extract_custom_types_table(doc):
        parse_custom_type_row(row, fork, config, out)

    code_blocks = extract_container_code_blocks(doc)
    # Poor man's dependency resolution strategy, by retry
    parse_container_code_blocks(code_blocks, fork, config, out)


def extract_custom_types_table(input: str) -> List[str]:
    matches = re.findall(
        r'## Custom types(.*?)\n[#]+ [^\n]+',
        input, re.DOTALL
    )
    if matches:
        return list(filter(
            lambda line: line.startswith('| `'),
            matches[0].strip().split('\n')
        ))
    else:
        return []


def parse_custom_type_row(row: str, fork: str, config: Dict, out: Dict):
    # Attempts to match the format "| `Slot` | `uint64` | a slot number |"
    pattern = r'\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|'
    match = re.search(pattern, row)
    if match:
        name, typename, comment = match.groups()
        out[fork][name] = get_type_schema(
            fork, typename, comment, config, out
        )
    else:
        raise ValueError("Custom type row format unknown: " + row)


def extract_container_code_blocks(input: str) -> List[str]:
    matches = re.findall(r'## Containers(.*?)(?:\n## [^\n]+|$)', input, re.DOTALL)
    if matches:
        python_code_blocks = re.findall(
            r'```python\n(.*?)\n```',
            matches[0], re.DOTALL
        )
        return python_code_blocks
    else:
        return []


def parse_container_code_blocks(
    code_blocks: List[str], fork: str, config: Dict, out: Dict
):
    unknown_code_blocks = []
    unknown_types = []
    for code in code_blocks:
        try:
            parse_container_code_block(code, fork, config, out)
        except UnknownType as e:
            unknown_types.append(str(e))
            unknown_code_blocks.append(code)

    if len(unknown_code_blocks) > 0:
        # Break out of the recursive loop if no type is resolved
        if len(unknown_code_blocks) < len(code_blocks):
            parse_container_code_blocks(unknown_code_blocks, fork, config, out)
        else:
            raise Exception("Unknwon types: ", ' '.join(unknown_types))


def parse_container_code_block(code: str, fork: str, config: Dict, out: Dict):
    match = re.search(r'^class (\w+)\(.*\):', code, re.MULTILINE)
    if match:
        class_name = match.group(1)
    else:
        # Not a container declaration codeblock
        return

    if class_name in config.get('ignore_classnames', {}):
        return

    properties = {}
    for line in re.findall(r"^\s+\w+.*:\s\w+.*$", code, re.MULTILINE):
        prop, prop_type = line.strip().split(':', 1)
        prop_type, comment = split_trailing_comment(prop_type)
        properties[prop] = get_type_schema(
            fork, prop_type, comment, config, out
        )
        config['dependants'].setdefault(prop_type, set()).add(class_name)
    out[fork][class_name] = {
        'type': 'object',
        'properties': properties,
    }
    # Need to track dependencies. If ExecutionHeader changes for a fork, the
    # dependant type BeaconState must be recreated for the that fork
    config['mutations'][fork].append(class_name)
    config['class_code'][class_name] = code


def parse_typename(input: str, fork: str, out: Dict) -> Dict:
    if input.startswith('Bitlist'):
        return {'$ref': '#/primitive/Bitlist'}

    if input.startswith('Bitvector'):
        return {'$ref': '#/primitive/Bitlist'}

    if input.startswith('ByteList'):
        return {'$ref': '#/primitive/ByteList'}

    if input.startswith('ByteVector'):
        return {'$ref': '#/primitive/ByteVector'}

    match = re.search(r'List\[(\w+),', input)
    if match:
        return {
            'type': 'array',
            'items': parse_typename(match.group(1), fork, out)
        }

    match = re.search(r'Vector\[(\w+),', input)
    if match:
        return {
            'type': 'array',
            'items': parse_typename(match.group(1), fork, out)
        }

    # Auto-generate Bytes type, but only once
    match = re.search(r'Bytes(\d+)', input)
    if match:
        if input not in out['primitive']:
            byte_len = int(match.group(1))
            out['primitive'][input] = bytes_type(byte_len)
        return {'$ref': f"#/primitive/{input}"}

    forks = list(out.keys())
    forks.reverse()
    for fork_r in forks:
        if input in out[fork_r]:
            return {'$ref': f"#/{fork_r}/{input}"}

    print(f"Type name not known {fork}: '{input}'", file=sys.stderr)
    raise UnknownType(f"Type name not known {fork} '{input}'")


def get_type_schema(
    fork: str, typename: str, comment: str, config: Dict, out: Dict,
) -> Dict:
    schema = parse_typename(typename, fork, out)

    # maybe add comment
    comment = comment.strip()
    if comment != "" and not should_exclude_comment(comment, config):
        if '$ref' in schema:
            # $ref syntax needs allOf to merge the referenced schema
            schema = {
                'allOf': [
                    schema,
                    {'description': comment}
                ]
            }
        else:
            schema['description'] = comment

    return schema


def should_exclude_comment(comment: str, config: Dict) -> bool:
    for regex in config.get('exclude_comments', []):
        if re.search(regex, comment):
            return True
    return False


def split_trailing_comment(s: str) -> Tuple[str, str]:
    parts = s.strip().split('#', 1)
    if len(parts) > 1:
        return parts[0].strip(), parts[1].strip()
    else:
        return parts[0].strip(), ""


class UnknownType(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"UnknownType: {self.message}"


def generate_hex_string(length):
    # Create an infinite loop over the characters
    looped_chars = itertools.cycle('0123456789abcdef')
    # Take the first N characters from the looped iterator
    return ''.join(next(looped_chars) for _ in range(length))


def bytes_type(byte_len: int) -> Dict:
    return {
        'type': 'string',
        'format': 'hex',
        'example': f"0x{generate_hex_string(byte_len)}",
        'pattern': f"^0x[a-fA-F0-9]{{{byte_len * 2}}}$",
    }
