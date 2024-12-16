from flask import Flask, request, jsonify
import re
from sympy import symbols, sympify, Eq, solve, factor
import requests  # Pour les requêtes HTTP

app = Flask(__name__)

SPRING_BOOT_API_URL = "http://localhost:8082/api/store-polynomial"

x = symbols('x')

def normalize_expression(expr):
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

@app.route('/process_polynomiall', methods=['POST'])
def process_polynomial():
    data = request.get_json()
    expression = data.get("expression", "")
    user_id = data.get("userId", None)

    if not user_id:
        return jsonify({"error": "userId is required."}), 400
    if not expression:
        return jsonify({"error": "Please provide a polynomial expression."}), 400

    normalized_expr = normalize_expression(expression)

    try:
        simplified_expr = sympify(normalized_expr).simplify()
        simplified_str = format_simplified_expression(simplified_expr)

        factored_expr = factor(simplified_expr)
        factored_str = format_simplified_expression(factored_expr)

        roots = solve(Eq(simplified_expr, 0), x)
        formatted_roots = [str(root.evalf()) for root in roots]

        result = {
            "simplifiedExpression": simplified_str,
            "factoredExpression": factored_str,
            "roots": formatted_roots,
            "userId": user_id
        }

        # Envoi des résultats à l'API Spring Boot
        spring_response = requests.post(SPRING_BOOT_API_URL, json=result)
        if spring_response.status_code == 200:
            return jsonify({"message": "Polynomial processed and stored successfully.", "result": result}), 200
        else:
            return jsonify({"error": "Failed to store polynomial in Spring Boot."}), spring_response.status_code
    except Exception as e:
        return jsonify({"error": f"Error processing polynomial: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5010)
