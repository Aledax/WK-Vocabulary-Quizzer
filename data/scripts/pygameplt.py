import pygame, matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

matplotlib.use('Agg')
plt.figure()

def create_graph_surface(figure):
    canvas = agg.FigureCanvasAgg(figure)
    canvas.draw()
    size = canvas.get_width_height()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba().tobytes()
    surface = pygame.image.fromstring(raw_data, size, "RGBA")
    return surface