from flask import Flask, request, jsonify
from sympy import symbols, Eq, solve, simplify, factor, I
import re
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Fonction pour convertir l'expression du format textuel en sympy

def parse_polynomial(poly_str):
    poly_str = re.sub(r'(\d+)x(\d+)', r'\1*x**\2', poly_str)

    poly_str = re.sub(r'(?<!\*)\b(\d)(x)', r'\1*\2', poly_str)  # Convertit 2x -> 2*x
    poly_str = re.sub(r'(?<!\*)\b(x)(\d)', r'\1**\2', poly_str)  # Convertit x2 -> x**2
    return poly_str

# Fonction pour retirer les * et convertir I en i dans les expressions

def format_expression(expr):
    formatted = re.sub(r'\*', '', str(expr))
    return formatted.replace('I', 'i')

@app.route('/process_polynomial', methods=['POST'])
def solve_polynomial():
    data = request.json
    expression = data.get('expression')
    user_id = data.get('userId')

    if not expression:
        return jsonify({"error": "No polynomial provided"}), 400

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    x = symbols('x')
    try:
        parsed_poly = parse_polynomial(expression)
        parsed_expr = eval(parsed_poly)

        # Résolution des racines
        eq = Eq(parsed_expr, 0)
        roots = solve(eq, x)
        roots = [format_expression(root) for root in roots]

        # Simplification
        simplified_expr = simplify(parsed_expr)

        # Factorisation
        factored_expr = factor(parsed_expr)

        # Préparer les données pour l'API externe
        payload = {
            "simplifiedExpression": format_expression(simplified_expr),
            "factoredExpression": format_expression(factored_expr),
            "roots": roots,
            "userId": user_id
        }

        # Envoyer les résultats à l'API externe pour stockage
        response = requests.post("http://spring-app:8082/api/store-polynomial", json=payload)

        if response.status_code == 200:
            return jsonify({
                "userId": user_id,
                "roots": roots,
                "simplifiedExpression": format_expression(simplified_expr),
                "factoredExpression": format_expression(factored_expr)
            })
        else:
            return jsonify({"error": "Failed to store polynomial", "details": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5110, debug=True)