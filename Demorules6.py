import json
from business_rules import run_all
from business_rules.actions import BaseActions, rule_action
from business_rules.variables import BaseVariables, string_rule_variable
from business_rules.fields import FIELD_TEXT

class ProjectVariables(BaseVariables):
    def __init__(self, project_data):
        self.project_data = project_data

    @string_rule_variable(label='ProjectFor')
    def ProjectFor(self):
        return self.project_data.get('ProjectFor')

    @string_rule_variable(label='PwCAccelerators')
    def PwCAccelerators(self):
        return self.project_data.get('PwCAccelerators')

class ProjectActions(BaseActions):
    def __init__(self):
        self.displayed_fields = []

    @rule_action(params={"fields": FIELD_TEXT})
    def display_fields(self, fields):
        self.displayed_fields.append(fields)

def load_rules():
    with open('newrules.json', 'r') as file:
        data = json.load(file)
    return data['rules']

project_data = {
    'ProjectFor': 'Services',
    'PwCAccelerators': 'Yes',
    'ProductName': 'PwC Analytics Suite'
}

rules = load_rules()

print("Processing Project Data:")
print(f"Project Data: {project_data}")

variables = ProjectVariables(project_data)
actions = ProjectActions()

run_all(rule_list=rules,
        defined_variables=variables,
        defined_actions=actions,
        stop_on_first_trigger=True)

if actions.displayed_fields:
    print("\nRules triggered:")
    for rule in rules:
        conditions_met = all(
            getattr(variables, condition['name'])() == condition['value']
            for condition in rule['conditions']['all']
        )
        if conditions_met:
            print("Rule conditions met:")
            for condition in rule['conditions']['all']:
                print(f"  - {condition['name']} is {condition['value']}")
    print(f"\nAction taken: {actions.displayed_fields[0]}")
    
    if "PwCAccelerator Flag" in actions.displayed_fields[0]:
        print(f"\nRelevant project information: {actions.displayed_fields[0]}")
    elif "ProductName" in actions.displayed_fields[0]:
        print(f"\nRelevant project information: ProductName: {project_data.get('ProductName', 'N/A')}")
else:
    print("No rules were triggered for this project data.")

print("\n" + "="*50 + "\n")