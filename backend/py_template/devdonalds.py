from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipe_name: str) -> Union[str | None]:

	# All hyphens (-) and underscores (_) are replaced with a whitespace. 
	recipe_name = re.sub(r'[-_]', ' ', recipe_name)

	# Food names can only contain letters and whitespaces.
	recipe_name = re.sub(r'[^A-Za-z\s]',  '', recipe_name)

	# Words in recipe_name are capitalized.
	recipe_name = ' '.join(word.capitalize() for word in recipe_name.split())


	# Consecutive whitespaces are reduced to a single whitespace where this also
	# includes leading and trailing whitespaces.
	recipe_name = re.sub(r'\s{2,}', ' ', recipe_name).strip()

	# If the input is an empty string, return None.
	if len(recipe_name) == 0:
		return None

	return recipe_name


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():	
	data = request.get_json()
	type = data.get('type')
	parsed_name = parse_handwriting(data.get('name'))

	if not parsed_name:
		return 'Name can not be empty', 400

	if type not in ['recipe', 'ingredient']:
		return 'Type can only be "recipe" or "ingredient"', 400
	elif type == 'ingredient' and data.get('cookTime') < 0:
		return 'CookTime can only be greater than or equal to 0', 400
	elif parsed_name in cookbook:
		return 'Entry names must be unique', 400
	elif type == 'recipe':
		required_items = data.get('requiredItems', [])
		required_item_names = set()
		for item in required_items:
			item_name = item.get('name')
			if item_name in required_item_names:
				return 'Recipe requiredItems can only have one element per name.', 400
			required_item_names.add(item_name)

	# Use data classes provided
	if type == 'recipe':
		required_items = [
            RequiredItem(name=item['name'], quantity=item['quantity'])
            for item in data.get('requiredItems', [])
        ]
		cookbook[parsed_name] = Recipe(name=parsed_name, required_items=required_items)
	elif type == 'ingredient':
		cookbook[parsed_name] = Ingredient(name=parsed_name, cook_time=data.get('cookTime', 0))

	return '', 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	recipe_name = request.args.get('name', None)
	parsed_name = parse_handwriting(recipe_name)

	entry = cookbook[parsed_name]
	if not entry:
		return 'A recipe with the corresponding name cannot be found.', 400
	elif entry.get('type') != 'recipe':
		return 'The searched name is NOT a recipe name.', 400

	total_cook_time = 0

# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
