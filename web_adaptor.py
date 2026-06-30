'''
Adaptador Web Real integrado con tu proyecto 'sudoku.py'.
Usa exactamente tus funciones matemáticas is_valid y find_empty para resolver desde la web.
'''
from flask import Flask, render_template_string, request, jsonify
import importlib
import sys

app = Flask(__name__)

# NOMBRE DE TU ARCHIVO ORIGINAL
NOMBRE_ARCHIVO_SUDOKU = 'sudoku'

try:
    modulo_sudoku = importlib.import_module(NOMBRE_ARCHIVO_SUDOKU)
except ImportError:
    modulo_sudoku = None

# =====================================================================
# ALGORITMO BACKTRACKING WEB (REUTILIZA TUS FUNCIONES ORIGINALES)
# =====================================================================
def resolver_web(matrix):
    """
    Ejecuta el algoritmo usando tus funciones lógicas exactas.
    Evitamos llamar a solve_with_backtracking() para que no se ejecute Pygame en Render.
    """
    # Usamos tu función original para buscar casilleros vacíos
    empty = modulo_sudoku.find_empty(matrix)
    if not empty:
        return True
    row, col = empty

    # Probamos números del 1 al 9 usando tu regla de validación original
    for num in range(1, 10):
        if modulo_sudoku.is_valid(matrix, num, (row, col)):
            matrix[row][col] = num

            # Llamada recursiva estándar
            if resolver_web(matrix):
                return True
            
            # Backtracking puro
            matrix[row][col] = 0

    return False

# =====================================================================
# INTERFAZ GRÁFICA INTERACTIVA HTML (CON JAVASCRIPT CORREGIDO c++)
# =====================================================================
HTML_SUDOKU = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resolutor de Sudoku - Web Adaptor</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; text-align: center; background-color: #f4f7f6; margin-top: 40px; }
        .contenedor { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); }
        h2 { color: #028090; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(9, 40px); gap: 1px; background-color: #bcbcbc; padding: 3px; border: 3px solid #333; }
        .grid input { width: 40px; height: 40px; text-align: center; font-size: 18px; font-weight: bold; border: 1px solid #e0e0e0; box-sizing: border-box; }
        
        /* Estilos visuales para los bloques 3x3 */
        .grid input:nth-child(3n) { border-right: 3px solid #333; }
        .grid input:nth-child(9n) { border-right: 1px solid #e0e0e0; }
        .grid input:nth-child(n+19):nth-child(-n+27),
        .grid input:nth-child(n+46):nth-child(-n+54) { border-bottom: 3px solid #333; }

        .btn-group { margin-top: 20px; display: flex; gap: 10px; justify-content: center; }
        button { padding: 12px 20px; background-color: #00a896; color: white; border: none; border-radius: 4px; font-size: 15px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #028090; }
        .clear-btn { background-color: #e63946; }
        .clear-btn:hover { background-color: #cb3234; }
        .status { margin-top: 15px; font-weight: bold; color: #028090; font-size: 1.1rem; }
    </style>
</head>
<body>
    <div class="contenedor">
        <h2>Resolutor de Sudoku</h2>
        <div class="grid" id="sudoku-grid"></div>
        <div class="btn-group">
            <button onclick="resolver()">Resolver Sudoku</button>
            <button class="clear-btn" onclick="limpiar()">Limpiar</button>
        </div>
        <div id="status" class="status"></div>
    </div>

    <script>
        const grid = document.getElementById('sudoku-grid');
        for (let i = 0; i < 81; i++) {
            const input = document.createElement('input');
            input.type = 'text';
            input.maxLength = 1;
            input.oninput = function() { this.value = this.value.replace(/[^1-9]/g, ''); };
            grid.appendChild(input);
        }

        function obtenerTablero() {
            const inputs = grid.getElementsByTagName('input');
            let tablero = [];
            let fila = [];
            for (let i = 0; i < 81; i++) {
                fila.push(inputs[i].value ? parseInt(inputs[i].value) : 0);
                if (fila.length === 9) {
                    tablero.push(fila);
                    fila = [];
                }
            }
            return tablero;
        }

        function setearTableroPlano(tableroPlano) {
            const inputs = grid.getElementsByTagName('input');
            for (let i = 0; i < 81; i++) {
                inputs[i].value = tableroPlano[i] !== 0 ? tableroPlano[i] : '';
            }
        }

        function resolver() {
            const tablero = obtenerTablero();
            const statusDiv = document.getElementById('status');
            statusDiv.innerText = "Resolviendo...";

            fetch('/api/resolver', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tablero: tablero })
            })
            .then(res => res.json())
            .then(data => {
                if (data.exito) {
                    setearTableroPlano(data.tablero.flat());
                    statusDiv.innerText = "¡Sudoku Resuelto";
                } else {
                    statusDiv.innerText = "Este Sudoku no tiene solución.";
                }
            })
            .catch(() => { statusDiv.innerText = "Error en el servidor."; });
        }

        function limpiar() {
            const inputs = grid.getElementsByTagName('input');
            for (let i = 0; i < 81; i++) inputs[i].value = '';
            document.getElementById('status').innerText = "";
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_SUDOKU)

@app.route('/api/resolver', methods=['POST'])
def resolver_api():
    data = request.get_json()
    tablero_web = data.get('tablero')

    if not modulo_sudoku:
        return jsonify({"exito": False, "mensaje": "No se pudo importar sudoku.py"}), 500

    try:
        # Clonamos la matriz recibida
        copia_tablero = [fila[:] for fila in tablero_web]
        
        # Ejecutamos tu motor de backtracking de forma segura
        ha_resuelto = resolver_web(copia_tablero)
        
        if ha_resuelto:
            return jsonify({"exito": True, "tablero": copia_tablero})
        else:
            return jsonify({"exito": False})
            
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)