from flask import Flask, request, jsonify
import re
from sympy import symbols, sympify, Eq, solve, factor

app = Flask(__name__)

# Variable symbolique pour le polynôme
x = symbols('x')
def normalize_expression(expr):
    # Remplacer les notations incorrectes
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
    data = request.get_json()  # Récupère les données JSON de la requête
    
    # Obtenir l'expression du polynôme
    expression = data.get("expression", "")
    
    if expression:
        # Normaliser l'expression avant de la passer à sympy
        normalized_expr = normalize_expression(expression)
        
        try:
            # Simplification du polynôme
            simplified_expr = sympify(normalized_expr)
            simplified_expr = simplified_expr.simplify()  # Appliquer la simplification
            simplified_str = format_simplified_expression(simplified_expr)
            
            # Factorisation symbolique
            factored_expr = factor(simplified_expr)
            factored_str = format_simplified_expression(factored_expr)
            
            # Calculer les racines du polynôme simplifié avec sympy
            roots = solve(Eq(simplified_expr, 0), x)
            
            # Formatage des racines en "a + bi" ou "a - bi"
            formatted_roots = []
            for root in roots:
                if root.is_complex:  # Si la racine est complexe
                    real_part = f"{root.as_real_imag()[0]:.4f}"
                    imaginary_part = f"{abs(root.as_real_imag()[1]):.4f}"
                    if root.as_real_imag()[1] >= 0:
                        formatted_root = f"{real_part} + {imaginary_part}i"
                    else:
                        formatted_root = f"{real_part} - {imaginary_part}i"
                else:  # Si la racine est réelle
                    formatted_root = f"{root.evalf():.4f}"
                
                formatted_roots.append(formatted_root)
            
            result = {
                "simplified_expression": simplified_str,
                "factored_expression": factored_str,
                "roots": formatted_roots
            }
        except Exception as e:
            return jsonify({"error": f"Erreur lors du calcul des racines : {str(e)}"}), 400
        
    else:
        return jsonify({"error": "Veuillez fournir une expression de polynôme."}), 400
    
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)