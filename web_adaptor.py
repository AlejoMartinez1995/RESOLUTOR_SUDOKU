'''
Adaptador Web Real integrado con tu proyecto 'sudoku.py'.
Usa exactamente tus funciones matemáticas is_valid y find_empty para resolver desde la web,
y añade un visualizador animado de backtracking client-side en tiempo real con control de velocidad.
'''
from flask import Flask, render_template_string, request, jsonify
import importlib
import os
import sys

app = Flask(__name__)

# NOMBRE DE TU ARCHIVO ORIGINAL
NOMBRE_ARCHIVO_SUDOKU = 'sudoku'

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    modulo_sudoku = importlib.import_module(NOMBRE_ARCHIVO_SUDOKU)
except ImportError:
    modulo_sudoku = None

def resolver_web(matrix):
    """
    Ejecuta el algoritmo en el backend usando tus funciones lógicas exactas.
    Reutilizado como fallback rápido o cuando se pide 'Resolver Instantáneo'.
    """
    if not modulo_sudoku:
        return False
    empty = modulo_sudoku.find_empty(matrix)
    if not empty:
        return True
    row, col = empty

    for num in range(1, 10):
        if modulo_sudoku.is_valid(matrix, num, (row, col)):
            matrix[row][col] = num
            if resolver_web(matrix):
                return True
            matrix[row][col] = 0
    return False

# =====================================================================
# INTERFAZ GRÁFICA INTERACTIVA HTML (TEMA OSCURO PREMIUM)
# =====================================================================
HTML_SUDOKU = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <title>Visualizador Sudoku Backtracking - Premium Edition</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #020617;
            --card-bg: rgba(15, 23, 42, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --primary-color: #06b6d4;
            --primary-hover: #0891b2;
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            
            --cell-orig-color: #f3f4f6;
            --cell-orig-bg: rgba(255, 255, 255, 0.02);
            --cell-solver-color: #38bdf8;
            --cell-tentative-color: #4ade80;
            --cell-tentative-bg: rgba(74, 222, 128, 0.15);
            --cell-backtrack-color: #f87171;
            --cell-backtrack-bg: rgba(248, 113, 113, 0.2);
        }

        body { 
            font-family: 'Outfit', sans-serif; 
            background: radial-gradient(circle at 50% 50%, #1e1b4b 0%, #020617 100%);
            color: var(--text-color);
            margin: 0;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            flex-direction: column;
        }

        .contenedor {
            background: var(--card-bg);
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid var(--border-color);
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
            display: flex;
            gap: 40px;
            max-width: 900px;
            width: 100%;
        }

        @media (max-width: 800px) {
            .contenedor {
                flex-direction: column;
                padding: 30px 20px;
                align-items: center;
            }
        }

        .panel-control {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 250px;
        }

        .panel-grid {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        h2 { 
            font-size: 2rem;
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 5px;
            background: linear-gradient(135deg, var(--primary-color) 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .sub {
            color: var(--text-muted);
            margin-bottom: 25px;
            font-size: 0.95rem;
        }

        /* Grilla del Sudoku */
        .grid { 
            display: grid; 
            grid-template-columns: repeat(9, 44px); 
            grid-template-rows: repeat(9, 44px);
            gap: 1px; 
            background-color: #334155; 
            padding: 3px; 
            border: 3px solid #475569; 
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .grid input { 
            width: 44px; 
            height: 44px; 
            text-align: center; 
            font-size: 20px; 
            font-weight: bold; 
            border: 1px solid #1e293b; 
            box-sizing: border-box; 
            background: #0f172a;
            color: var(--cell-orig-color);
            outline: none;
            transition: all 0.2s ease;
        }

        .grid input:focus {
            background: rgba(6, 182, 212, 0.1);
            border-color: var(--primary-color);
        }
        
        /* Líneas gruesas de cuadrantes 3x3 */
        .grid input:nth-child(3n) { border-right: 3px solid #475569; }
        .grid input:nth-child(9n) { border-right: 1px solid #1e293b; }
        
        .grid input:nth-child(n+19):nth-child(-n+27),
        .grid input:nth-child(n+46):nth-child(-n+54) { border-bottom: 3px solid #475569; }

        /* Clases de estados del solucionador */
        .cell-original {
            color: var(--cell-orig-color) !important;
            background: var(--cell-orig-bg) !important;
        }
        .cell-tentative {
            color: var(--cell-tentative-color) !important;
            background: var(--cell-tentative-bg) !important;
            border-color: var(--cell-tentative-color) !important;
        }
        .cell-backtrack {
            color: var(--cell-backtrack-color) !important;
            background: var(--cell-backtrack-bg) !important;
            border-color: var(--cell-backtrack-color) !important;
        }
        .cell-solved {
            color: var(--cell-solver-color) !important;
            background: rgba(56, 189, 248, 0.05) !important;
        }

        /* Controles */
        .control-group {
            margin-bottom: 20px;
            text-align: left;
        }

        label {
            display: block;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 8px;
            font-weight: 600;
        }

        .btn-group { 
            display: flex; 
            gap: 12px; 
            flex-wrap: wrap;
            margin-top: 15px; 
        }

        button { 
            padding: 12px 20px; 
            background: linear-gradient(135deg, var(--primary-color) 0%, #3b82f6 100%); 
            color: #020617; 
            border: none; 
            border-radius: 8px; 
            font-size: 0.95rem; 
            cursor: pointer; 
            font-weight: 700; 
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2);
            flex: 1;
            min-width: 120px;
        }

        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.35);
            filter: brightness(1.1);
        }

        .btn-clear {
            background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
            color: var(--text-color);
            box-shadow: none;
            border: 1px solid var(--border-color);
        }

        .btn-clear:hover {
            background: linear-gradient(135deg, #475569 0%, #334155 100%);
            box-shadow: none;
        }

        /* Slider de velocidad */
        .slider-wrapper {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        input[type="range"] {
            flex: 1;
            accent-color: var(--primary-color);
            cursor: pointer;
        }

        .preset-select {
            width: 100%;
            padding: 12px;
            background: rgba(15, 23, 42, 0.6);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            outline: none;
            cursor: pointer;
            font-size: 0.95rem;
        }

        .status { 
            margin-top: 20px; 
            font-weight: 600; 
            color: var(--primary-color); 
            font-size: 1.1rem; 
            min-height: 25px;
        }

        .status.error {
            color: #ef4444;
        }
        
        .status.success {
            color: #4ade80;
        }
    </style>
</head>
<body>
    <div class="contenedor">
        <div class="panel-control">
            <h2>Sudoku Solver</h2>
            <div class="sub">Visualizador interactivo de algoritmos de backtracking.</div>

            <div class="control-group">
                <label for="presets">Tableros de Ejemplo</label>
                <select id="presets" class="preset-select" onchange="cargarPreset()">
                    <option value="empty">Tablero Vacío</option>
                    <option value="easy" selected>Nivel Fácil (Predeterminado)</option>
                    <option value="medium">Nivel Medio</option>
                    <option value="hard">Nivel Difícil</option>
                </select>
            </div>

            <div class="control-group">
                <label>Velocidad de Animación</label>
                <div class="slider-wrapper">
                    <input type="range" id="speed-slider" min="1" max="300" value="50" oninput="updateSpeedText()">
                    <span id="speed-text" style="font-family: monospace; width: 60px;">50ms</span>
                </div>
            </div>

            <div class="btn-group">
                <button id="btn-visual" onclick="iniciarVisualizacion()">Ver Algoritmo</button>
                <button id="btn-inst" class="btn-clear" onclick="resolverInstantaneo()">Instantáneo</button>
            </div>

            <div class="btn-group">
                <button id="btn-pause" class="btn-clear" style="display: none;" onclick="togglePause()">Pausar</button>
                <button class="btn-clear" onclick="limpiarTablero()">Limpiar Todo</button>
            </div>

            <div id="status" class="status"></div>
        </div>

        <div class="panel-grid">
            <div class="grid" id="sudoku-grid"></div>
        </div>
    </div>

    <script>
        const grid = document.getElementById('sudoku-grid');
        const inputs = [];
        
        // Inicialización de la Grilla de 81 Casilleros
        for (let i = 0; i < 81; i++) {
            const input = document.createElement('input');
            input.type = 'text';
            input.maxLength = 1;
            input.oninput = function() {
                this.value = this.value.replace(/[^1-9]/g, '');
                if (this.value) {
                    this.className = 'cell-original';
                } else {
                    this.className = '';
                }
            };
            grid.appendChild(input);
            inputs.push(input);
        }

        // Tableros de Ejemplo
        const presets = {
            empty: Array(81).fill(0),
            easy: [
                5, 3, 0, 0, 7, 0, 0, 0, 0,
                6, 0, 0, 1, 9, 5, 0, 0, 0,
                0, 9, 8, 0, 0, 0, 0, 6, 0,
                8, 0, 0, 0, 6, 0, 0, 0, 3,
                4, 0, 0, 8, 0, 3, 0, 0, 1,
                7, 0, 0, 0, 2, 0, 0, 0, 6,
                0, 6, 0, 0, 0, 0, 2, 8, 0,
                0, 0, 0, 4, 1, 9, 0, 0, 5,
                0, 0, 0, 0, 8, 0, 0, 7, 9
            ],
            medium: [
                3, 0, 6, 5, 0, 8, 4, 0, 0,
                5, 2, 0, 0, 0, 0, 0, 0, 0,
                0, 8, 7, 0, 0, 0, 0, 3, 1,
                0, 0, 3, 0, 1, 0, 0, 8, 0,
                9, 0, 0, 8, 6, 3, 0, 0, 5,
                0, 5, 0, 0, 9, 0, 6, 0, 0,
                1, 3, 0, 0, 0, 0, 2, 5, 0,
                0, 0, 0, 0, 0, 0, 0, 7, 4,
                0, 0, 5, 2, 0, 6, 3, 0, 0
            ],
            hard: [
                0, 0, 0, 6, 0, 0, 4, 0, 0,
                7, 0, 0, 0, 0, 3, 6, 0, 0,
                0, 0, 0, 0, 9, 1, 0, 8, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 5, 0, 1, 8, 0, 0, 0, 3,
                0, 0, 0, 3, 0, 6, 0, 4, 5,
                0, 4, 0, 2, 0, 0, 0, 6, 0,
                9, 0, 3, 0, 0, 0, 0, 0, 0,
                0, 2, 0, 0, 0, 0, 1, 0, 0
            ]
        };

        function setearTablero(arr) {
            for (let i = 0; i < 81; i++) {
                inputs[i].value = arr[i] !== 0 ? arr[i] : '';
                inputs[i].className = arr[i] !== 0 ? 'cell-original' : '';
                inputs[i].disabled = false;
            }
        }

        function cargarPreset() {
            detenerVisualizacion();
            const val = document.getElementById('presets').value;
            setearTablero(presets[val]);
            document.getElementById('status').innerText = "";
        }

        // Cargar por defecto el nivel fácil
        cargarPreset();

        function updateSpeedText() {
            const val = document.getElementById('speed-slider').value;
            document.getElementById('speed-text').innerText = `${val}ms`;
        }

        // --- SISTEMA DE VISUALIZACIÓN INTERACTIVA (Backtracking en Cliente) ---
        let runningVisual = false;
        let isPaused = false;
        let originalBoardMask = []; // Guarda qué celdas eran originales del usuario
        let solveBoard = [];

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        function togglePause() {
            isPaused = !isPaused;
            document.getElementById('btn-pause').innerText = isPaused ? "Reanudar" : "Pausar";
            document.getElementById('status').innerText = isPaused ? "Resolución Pausada" : "Resolviendo...";
        }

        function detenerVisualizacion() {
            runningVisual = false;
            isPaused = false;
            document.getElementById('btn-pause').style.display = "none";
            document.getElementById('btn-visual').innerText = "Ver Algoritmo";
            document.getElementById('btn-inst').disabled = false;
            inputs.forEach((inp, idx) => {
                if (inp.disabled && !originalBoardMask[idx]) {
                    inp.disabled = false;
                }
            });
        }

        function obtenerTableroMatriz() {
            let matriz = [];
            let fila = [];
            for (let i = 0; i < 81; i++) {
                fila.push(inputs[i].value ? parseInt(inputs[i].value) : 0);
                if (fila.length === 9) {
                    matriz.push(fila);
                    fila = [];
                }
            }
            return matriz;
        }

        function validarSudokuInicial(matriz) {
            // Verifica que los números colocados inicialmente no violen las reglas básicas
            for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; c++) {
                    const val = matriz[r][c];
                    if (val !== 0) {
                        // Temporalmente vaciamos para ver si es válido
                        matriz[r][c] = 0;
                        if (!isValidJS(matriz, val, r, c)) {
                            return false;
                        }
                        matriz[r][c] = val;
                    }
                }
            }
            return true;
        }

        async function iniciarVisualizacion() {
            if (runningVisual) {
                detenerVisualizacion();
                document.getElementById('status').innerText = "Visualización cancelada.";
                return;
            }

            const matriz = obtenerTableroMatriz();
            if (!validarSudokuInicial(matriz)) {
                const status = document.getElementById('status');
                status.className = "status error";
                status.innerText = "Sudoku inválido en su configuración inicial.";
                return;
            }

            // Deshabilitar inputs
            originalBoardMask = inputs.map(inp => inp.value !== '');
            inputs.forEach(inp => inp.disabled = true);
            
            solveBoard = matriz;
            runningVisual = true;
            isPaused = false;
            
            document.getElementById('btn-visual').innerText = "Detener";
            document.getElementById('btn-pause').style.display = "inline-block";
            document.getElementById('btn-pause').innerText = "Pausar";
            document.getElementById('btn-inst').disabled = true;
            
            const statusDiv = document.getElementById('status');
            statusDiv.className = "status";
            statusDiv.innerText = "Resolviendo...";

            const exito = await solveBacktrackingVisual();
            
            detenerVisualizacion();
            
            if (exito) {
                statusDiv.className = "status success";
                statusDiv.innerText = "¡Sudoku Resuelto con Éxito!";
                // Colorear números generados en azul
                for (let i = 0; i < 81; i++) {
                    if (!originalBoardMask[i]) inputs[i].className = 'cell-solved';
                }
            } else {
                statusDiv.className = "status error";
                statusDiv.innerText = "Este Sudoku no tiene solución.";
            }
        }

        // Lógica de backtracking interactiva asíncrona
        async function solveBacktrackingVisual() {
            if (!runningVisual) return false;

            const empty = findEmptyJS(solveBoard);
            if (!empty) return true;
            const [row, col] = empty;
            const idx = row * 9 + col;

            for (let num = 1; num <= 9; num++) {
                if (!runningVisual) return false;

                // Loop para esperar si está pausado
                while (isPaused && runningVisual) {
                    await sleep(100);
                }

                if (isValidJS(solveBoard, num, row, col)) {
                    solveBoard[row][col] = num;
                    inputs[idx].value = num;
                    inputs[idx].className = 'cell-tentative';
                    
                    const delay = parseInt(document.getElementById('speed-slider').value);
                    await sleep(delay);

                    if (await solveBacktrackingVisual()) {
                        return true;
                    }

                    if (!runningVisual) return false;

                    while (isPaused && runningVisual) {
                        await sleep(100);
                    }

                    solveBoard[row][col] = 0;
                    inputs[idx].value = '';
                    inputs[idx].className = 'cell-backtrack';
                    
                    await sleep(Math.min(delay, 20)); // pausa rápida en retroceso
                }
            }
            return false;
        }

        // Funciones auxiliares en JS
        function findEmptyJS(board) {
            for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; c++) {
                    if (board[r][c] === 0) return [r, c];
                }
            }
            return null;
        }

        function isValidJS(board, num, row, col) {
            for (let i = 0; i < 9; i++) {
                if (board[row][i] === num && i !== col) return false;
                if (board[i][col] === num && i !== row) return false;
            }
            const boxRow = Math.floor(row / 3) * 3;
            const boxCol = Math.floor(col / 3) * 3;
            for (let r = boxRow; r < boxRow + 3; r++) {
                for (let c = boxCol; c < boxCol + 3; c++) {
                    if (board[r][c] === num && (r !== row || c !== col)) return false;
                }
            }
            return true;
        }

        // --- RESOLUCIÓN INSTANTÁNEA (Mediante backend Flask/Python) ---
        function resolverInstantaneo() {
            detenerVisualizacion();
            const tablero = obtenerTableroMatriz();
            
            if (!validarSudokuInicial(tablero)) {
                const status = document.getElementById('status');
                status.className = "status error";
                status.innerText = "Sudoku inválido en su configuración inicial.";
                return;
            }

            const statusDiv = document.getElementById('status');
            statusDiv.className = "status";
            statusDiv.innerText = "Resolviendo instantáneamente...";

            fetch('/api/resolver', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tablero: tablero })
            })
            .then(res => res.json())
            .then(data => {
                if (data.exito) {
                    const originalMask = inputs.map(inp => inp.value !== '');
                    const flatSolved = data.tablero.flat();
                    
                    for (let i = 0; i < 81; i++) {
                        inputs[i].value = flatSolved[i];
                        if (originalMask[i]) {
                            inputs[i].className = 'cell-original';
                        } else {
                            inputs[i].className = 'cell-solved';
                        }
                    }
                    statusDiv.className = "status success";
                    statusDiv.innerText = "¡Resuelto en backend con éxito!";
                } else {
                    statusDiv.className = "status error";
                    statusDiv.innerText = "Este Sudoku no tiene solución.";
                }
            })
            .catch(() => { 
                statusDiv.className = "status error";
                statusDiv.innerText = "Error al conectar con el servidor."; 
            });
        }

        function limpiarTablero() {
            detenerVisualizacion();
            inputs.forEach(inp => {
                inp.value = '';
                inp.className = '';
                inp.disabled = false;
            });
            document.getElementById('presets').value = 'empty';
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
        copia_tablero = [fila[:] for fila in tablero_web]
        ha_resuelto = resolver_web(copia_tablero)
        
        if ha_resuelto:
            return jsonify({"exito": True, "tablero": copia_tablero})
        else:
            return jsonify({"exito": False})
            
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
