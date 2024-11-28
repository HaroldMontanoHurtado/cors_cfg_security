import os
import ast
import astor
from itertools import combinations


class MutationTransformer(ast.NodeTransformer):
    def __init__(self, changes):
        self.changes = changes

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name) and node.targets[0].id in self.changes:
            new_value = ast.parse(self.changes[node.targets[0].id]).body[0].value
            return ast.copy_location(ast.Assign(targets=node.targets, value=new_value), node)
        return node


def mutate_class(class_code, changes, output_file):
    tree = ast.parse(class_code)
    transformer = MutationTransformer(changes)
    transformed_tree = transformer.visit(tree)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(astor.to_source(transformed_tree))


cors_config_code = '''
class CORSConfig:
    ORIGINS = ['http://example.com', 'http://another-example.com']
    METHODS = ['GET', 'POST', 'PUT', 'DELETE']
    ALLOW_HEADERS = ['Authorization', 'Content-Type']
    SUPPORTS_CREDENTIALS = False
    MAX_AGE = 3600
    SEND_WILDCARD = False
    AUTOMATIC_OPTIONS = False
    VARY_HEADER = True
'''

app_config_code = '''
class AppConfig:
    API_KEY = "your_secret_api_key"
'''

cors_changes = [
    {'ORIGINS': "['*']"},
    {'METHODS': "['*']"},
    {'ALLOW_HEADERS': "['*']"},
    {'SUPPORTS_CREDENTIALS': "True"},
    {'MAX_AGE': "86400"},
    {'SEND_WILDCARD': "True"},
    {'AUTOMATIC_OPTIONS': "True"},
    {'VARY_HEADER': "False"}
]

app_changes = [
    {'API_KEY': '""'}
]

# Generar mutaciones individuales para CORSConfig
for i, change in enumerate(cors_changes):
    output_file = f'mutants/cors_config_mutation_{i + 1}.py'
    mutate_class(cors_config_code, change, output_file)

# Generar mutaciones individuales para AppConfig
for i, change in enumerate(app_changes):
    output_file = f'mutants/app_config_mutation_{i + 1}.py'
    mutate_class(app_config_code, change, output_file)


def combine_mutations(class_code, mutation_list, output_prefix):
    num_mutations = len(mutation_list)
    for r in range(2, num_mutations + 1):  # Combinaciones de 2 a n mutaciones
        for combo in combinations(range(num_mutations), r):
            combined_changes = {}
            for idx in combo:
                combined_changes.update(mutation_list[idx])
            output_file = f'mutants/{output_prefix}_mutation_combined_{"_".join(map(str, combo))}.py'
            mutate_class(class_code, combined_changes, output_file)


# Combinaciones de mutaciones para CORSConfig
combine_mutations(cors_config_code, cors_changes, 'cors_config')

# Combinaciones de mutaciones para AppConfig
combine_mutations(app_config_code, app_changes, 'app_config')
