'''
Adaptador Genérico para el Resolutor de Sudoku (web_adaptor.py)
Expone tu lógica de resolución en una grilla interactiva de 9x9.
'''
from flask import Flask, render_template_string, request, jsonify
import importlib
import sys

app = Flask(__name__)

# CONFIGURACIÓN MANUAL: Nombre de tu archivo original de Sudoku sin el .py
NOMBRE_ARCHIVO_SUDOKU = 'sudoku' 

try:
    modulo_sudoku = importlib.import_module(NOMBRE_ARCHIVO_SUDOKU)
except ImportError:
    modulo_sudoku = None

HTML_SUDOKU = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resolutor de Sudoku - Web</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; text-align: center; background-color: #f4f7f6; margin-top: 40px; }
        .contenedor { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); }
        h2 { color: #028090; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(9, 40px); gap: 2px; background-color: #333; padding: 4px; border-radius: 4px; }
        .grid input { width: 40px; height: 40px; text-align: center; font-size: 18px; font-weight: bold; border: none; box-sizing: border-box; }
        /* Bordes gruesos para separar las regiones de 3x3 */
        .grid input:nth-child(3n) { border-right: 2px solid #333; }
        .grid input:nth-child(9n) { border-right: none; }
        .btn-group { margin-top: 20px; display: flex; gap: 10px; justify-content: center; }
        button { padding: 12px 20px; background-color: #00a896; color: white; border: none; border-radius: 4px; font-size: 15px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #028090; }
        .clear-btn { background-color: #e63946; }
        .clear-btn:hover { background-color: #cb3234; }
        .status { margin-top: 15px; font-weight: bold; color: #028090; }
    </style>
</head>
<body>
    <div class="contenedor">
        <h2>Resolutor de Sudoku</h2>
        <div class="grid" id="sudoku-grid">
            </div>
        <div class="btn-group">
            <button onclick="resolver()">Resolver Sudoku</button>
            <button class="clear-btn" onclick="limpiar()">Limpiar</button>
        </div>
        <div id="status" class="status"></div>
    </div>

    <script>
        // Crear la grilla de 9x9 inputs
        const grid = document.getElementById('sudoku-grid');
        for (let i = 0; i < 81; i++) {
            const input = document.createElement('input');
            input.type = 'text';
            input.maxLength = 1;
            // Bloquear que metan letras
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

        function setearTablero(tablero) {
            const inputs = grid.getElementsByTagName('input');
            let index = 0;
            for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; r++) { // Corrección para iterar correctamente sobre la matriz plana
                    inputs[index].value = tablero[r][c] !== 0 ? tablero[r][c] : '';
                    index++;
                }
            }
        }

        // JS corregido y simplificado para recorrer los 81 inputs
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
                    // Aplanamos la matriz devuelta por Python para rellenar los inputs fácilmente
                    setearTableroPlano(data.tablero.flat());
                    statusDiv.innerText = "¡Sudoku Resuelto!";
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
    tablero_usuario = data.get('tablero') # Recibe una lista de 9 listas (matriz de 9x9)

    if not modulo_sudoku:
        return jsonify({"exito": False, "mensaje": "Módulo original no encontrado"}), 500

    try:
        # Buscamos la función de resolución dentro de tu script original.
        # Ajustá 'resolver_sudoku' si tu función principal se llama diferente (ej: 'solve')
        funcion_resolver = getattr(modulo_sudoku, 'resolver_sudoku', None) or getattr(modulo_sudoku, 'solve', None)
        
        if funcion_resolver:
            # Duplicamos el tablero para no romper el original durante la ejecución
            copia_tablero = [fila[:] for fila in tablero_usuario]
            
            # Ejecutamos tu algoritmo de Backtracking
            resultado = funcion_resolver(copia_tablero)
            
            # Si tu función devuelve True/False y modifica la matriz in-place:
            if resultado is True or resultado is None:
                return jsonify({"exito": True, "tablero": copia_tablero})
            # Si tu función directamente devuelve la matriz resuelta:
            elif isinstance(resultado, list):
                return jsonify({"exito": True, "tablero": resultado})
                
        return jsonify({"exito": False})
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)