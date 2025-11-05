world =[[],[]]

def add_object(o,depth=0):
    global world
    world[depth].append(o)

def add_objects(ol, depth=0):
    world[depth] += ol

def update():
    for o in world:
        o.update()

def render():
    for o in world:
        o.draw()