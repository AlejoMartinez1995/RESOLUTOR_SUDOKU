'''Una interfaz gráfica (GUI) que resuelve automáticamente los rompecabezas de Sudoku.'''

import pygame
import sys
import time
import numpy as np

# Inicializamos Pygame
pygame.init()

# Configuramos la ventana
WIDTH = 540
HEIGHT = WIDTH + 50  # Espacio adicional para el texto de instrucciones
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver")

# Definimos colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Definimos la fuente
FONT = pygame.font.SysFont('comicsans', 40)
FONT_BUTTON = pygame.font.SysFont('comicsans', 30)

# Definimos el tablero de Sudoku (0 representa celdas vacías)
board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Copia del tablero para poder trabajar con él sin modificar el original
board_copy = [fila[:] for fila in board]

def is_valid(m, num, pos):
    """Verifica si un numero puede ser colocado en la posicion dada del tablero."""
    
    # Verifica la fila
    for f in range(len(m[0])):
        if m[pos[0]][f] == num and pos[1] != f:
            return False
        
    # Verifico la columna
    for c in range(len(m)):
        if m[c][pos[1]] == num and pos[0] != c:
            return False
        
    # Verifico el cuadrante 3x3
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for c in range(box_y * 3, box_y * 3 + 3):
        for f in range(box_x * 3, box_x * 3 + 3):
            if m[c][f] == num and (c, f) != pos:
                return False
            
    return True

def find_empty(m):
    """Encuentra una celda vacia en el tablero y devuelve su posicion (fila, columna):"""
    for f in range(len(m)):
        for c in range(len(m[0])):
            if m[f][c] == 0:
                return (f, c) #fila, columna
    return None

def draw_grid():
    """Dibuja la cuadricula del tablero de Sudoku"""
    distanse = WIDTH // 9
    for f in range(10):
        # Cada 3 lineas dibujamos una linea mas gruesa para separar los cuadrantes 3x3
        thickness = 4 if f % 3 == 0 else 1
        # Lineas horizontales
        pygame.draw.line(WINDOW, BLACK, (0, f * distanse), (WIDTH, f * distanse), thickness)
        # Lineas verticales
        pygame.draw.line(WINDOW, BLACK, (f * distanse, 0), (f * distanse, WIDTH), thickness)

def draw_numbers(color_actualizar=None, celda_actualizar=None):
    """dibuja los numeros en el tablero y resalta la celda en evaluacion."""

    distanse = WIDTH // 9
    for f in range(9):
        for c in range(9):
            num = board_copy[f][c]
            if num != 0:
            # Si es un numero original, se queda en negro. Si es del algoritmo, cambia de color.
                if board[f][c] != 0:
                    color = BLACK
                else:
                    color = color_actualizar if (f, c) == celda_actualizar else BLUE

                text = FONT.render(str(num), True, color)
                # Centrar el texto en la celda
                x = c * distanse + (distanse // 2 - text.get_width() // 2)
                y = f * distanse + (distanse // 2 - text.get_height() // 2)
                WINDOW.blit(text, (x, y))

def refresh_screen(cell=None, color=BLUE):
    """Refresca los gráficos en cada paso del algoritmo."""
    WINDOW.fill(WHITE)
    draw_grid()
    draw_numbers(color, cell)

    # CALCULOS DINÁMICOS:
    text_instruction = FONT_BUTTON.render("Presiona ESPACIO para resolver", True, BLACK)
    # Centramos el texto horizontalmente en la ventana
    x_pos = (WIDTH // 2) - (text_instruction.get_width() // 2)
    # Lo colocamos en la mitad del espacio extra que dejamos abajo
    y_pos = WIDTH + ((HEIGHT - WIDTH) // 2) - (text_instruction.get_height() // 2)

    WINDOW.blit(text_instruction, (x_pos, y_pos))

    pygame.display.update()

def solve_with_backtracking():
    """Algoritmo de backtraking que interactua con Pygame para la animacion del proceso de solucion."""

    # Manejo de eventos basico durante la resolucion para que no se congele la ventana
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Buscamos una celda vacia
    empty = find_empty(board_copy)
    if not empty:
        return True # Si no hay celdas vacias, el tablero esta completo
    else:
        row, col = empty

    # Probamos numeros del 1 al 9
    for num in range(1, 10):
        if is_valid(board_copy, num, (row, col)):
            board_copy[row][col] = num

            # Dibujar en VERDE indicando que el numero es "tentativamente valido"
            refresh_screen((row, col), GREEN)
            time.sleep(0.05) # Pausa para visualizar el proceso

            if solve_with_backtracking():
                return True
            
            # Si el algoritmo falla mas adelante, hace BACKTRACKING y borra el numero, dibujando en ROJO
            board_copy[row][col] = 0

            # Dibujar en ROJO indicando que se abandona la soluicion de esa celda
            refresh_screen((row, col), RED)
            time.sleep(0.02) # Pausa para visualizar el proceso

    return False

def main():
    """Funcion principal que maneja el buncle de eventos y la logica del programa."""
    running = True
    done = False

    while running:
        WINDOW.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not done:
                    # Resolvemos el Sudoku con backtracking
                    solve_with_backtracking()
                    done = True

        # Manntener el dibujo activo antes y despues de la resolucion
        refresh_screen()
        

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()  