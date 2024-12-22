from flask import Flask, request, jsonify
from flask_cors import CORS  # Importer CORS
import re
from sympy import symbols, sympify, Eq, solve, factor
import requests

app = Flask(__name__)
CORS(app)  # Permettre CORS sur toutes les routes de l'application

# Variable symbolique pour le polynôme
x = symbols('x')

# URL de l'API Spring Boot
SPRING_BOOT_API_URL = "http://localhost:8082/api/store-polynomial"

def normalize_expression(expr):
    # Normalisation de l'expression polynomiale
    expr = re.sub(r'x(\d+)', r'x^\1', expr)
    expr = expr.replace('x^', 'x**')
    expr = re.sub(r'(?<=\d)(x)', r'*x', expr)
    expr = re.sub(r'(?<=\d)(\()', r'*(', expr)
    expr = re.sub(r'([a-zA-Z0-9])\+', r'\1 +', expr)
    expr = re.sub(r'(\+|\-)\s*', r' \1 ', expr)
    expr = expr.replace('**1', '')
    return expr

def format_simplified_expression(expr):
    expr_str = str(expr)
    expr_str = expr_str.replace('**', '')
    expr_str = re.sub(r'(\d)(x\*)', r'\1x', expr_str)
    expr_str = re.sub(r'\*', '', expr_str)
    expr_str = expr_str.replace('x^1', 'x')
    expr_str = re.sub(r'(\+|\-)1x', r'\1x', expr_str)
    return expr_str

@app.route('/process_polynomial', methods=['POST'])
def process_polynomial():
    data = request.get_json()
    expression = data.get("expression", "")
    user_id = data.get("userId", "")  # Get userId from the request

    if not expression:
        return jsonify({"error": "Veuillez fournir une expression de polynôme."}), 400

    normalized_expr = normalize_expression(expression)

    try:
        # Simplification du polynôme
        simplified_expr = sympify(normalized_expr).simplify()
        simplified_str = format_simplified_expression(simplified_expr)

        # Factorisation
        factored_expr = factor(simplified_expr)
        factored_str = format_simplified_expression(factored_expr)

        # Résolution des racines
        roots = solve(Eq(simplified_expr, 0), x)
        formatted_roots = [str(root.evalf()) for root in roots]

        # Directly return the response with userId and roots
        return jsonify({
            "userId": user_id,
            "roots": formatted_roots, 
             "simplifiedExpression": simplified_str,
            "factoredExpression": factored_str
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors du traitement : {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5110)
