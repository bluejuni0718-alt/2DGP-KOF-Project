world =[]

def add_object(o):
    global world
    world.append(o)

def update():
    for o in world:
        o.update()

def render():
    for o in world:
        o.draw()