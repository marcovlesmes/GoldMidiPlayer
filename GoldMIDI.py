import pygame, sys, os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

pygame.init()

# Windows Setup
windowsSize = (697, 383)
pygame.display.set_caption('GoldMidiPlayer')
screen = pygame.display.set_mode(windowsSize)
buttons = []
gui = []
midi = pygame.mixer.music
clock = pygame.time.Clock()
playlist = []
debug = False

"""
class GUI():
    def __init__(self, config=config[0]):
        self.buttons = config[0]
        self.images = config[1]

class NewSprite(pygame.sprite.Sprite):
    def __init__(self, filename):
        pygame.sprite.Sprite.__init__(self)
        self.buttons = []
        self.buttons.append(create_button(filename))
        self.gui = []
        self.gui.append(create_image(filename))
        # self.images = []
        # self.images.append(loadImage(filename))
        # self.image = pygame.Surface.copy(self.images[0])
        # self.currentImage = 0
        # self.rect = self.image.get_rect()
        # self.rect.topleft = (0, 0)
        # self.mask = pygame.mask.from_surface(self.image)
        # self.angle = 0
        # self.scale = 1
        # self.originalWidth = self.rect.width
        # self.originalHeight = self.rect.height

    def add_image(self, filename):
        self.gui.append(create_image(filename))

    def move(self, xpos, ypos, centre=False):
        if centre:
            self.rect.center = [xpos, ypos]
        else:
            self.rect.topleft = [xpos, ypos]
"""


"""
Registra la creacion de cada imagen
"""


def create_image(name, coord):
    image = pygame.image.load(os.path.join('imgs', name + '.png'))
    gui.append([image, coord])


"""
Registra la creacion de cada boton.
name: nombre de la imagen y del boton.
coord: [left, top, width, height]
function: funcion a llamar cuando se presione
image: Es una imagen o una zona.
Si se encuentra debug activo (True) se muestran las zonas de los botones
"""


def create_button(name, coord, function, image=False):
    if image:
        image = pygame.image.load(os.path.join('imgs', name + '.png'))
    else:
        size = (coord[2], coord[3])
        image = pygame.Surface(size, pygame.SRCALPHA)
        if debug:
            image.fill((255, 255, 0, 60))
    buttons.append([coord, function, image])


"""
Reproduce el archivo cargado o abre la ventana para cargarlo
"""


def play():
    if len(playlist) == 0:
        open_new_midi()
    else:
        midi.play()


"""
Lanza la interfaz de windows para cargar un nuevo archivo
"""


def open_new_midi():
    Tk().withdraw()
    midi.stop()
    new_midi = askopenfilename()

    if new_midi:
        if new_midi.find('.mid', -4) > 5:
            playlist.append(new_midi)
            midi.load(new_midi)
            midi.play()


"""
Verifica de tener un evento en el mouse sobre que posicion se registro el evento
"""


def button_pressed(x, y):
    for button in buttons:
        left, top, width, height = button[0]

        if left < x < (width + left) and top < y < (height + top):
            button[1]()


"""
Redibuja la pantalla
"""


def refresh_screen():
    screen.fill((0, 0, 0))
    for image in gui:
        screen.blit(image[0], image[1])
    for button in buttons:
        screen.blit(button[2], (button[0][0], button[0][1]))


"""
Registra los objetos de la Interface
"""


def draw_main_screen():
    create_image('background', (0, 0))
    create_button('play', (485, 217, 28, 16), play)
    create_button('pause', (0, 217, 28, 16), midi.pause)
    create_button('stop', (455, 217, 28, 16), midi.stop)
    create_button('open_file', (555, 196, 90, 43), open_new_midi)


draw_main_screen()
myriadProFont = pygame.font.SysFont("comicsansms", 48)
buttonPressed = 'None Button Pressed'
helloWorld = myriadProFont.render(buttonPressed, 1, (255, 0, 255), (255, 255, 255))


def update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()
        button_pressed(x, y)

    refresh_screen()
    pygame.display.update()


while 1:
    clock.tick(40)
    update()
