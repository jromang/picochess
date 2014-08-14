from flask_frozen import Freezer
from picoweb import picoweb

freezer = Freezer(picoweb)

if __name__ == '__main__':
    freezer.freeze()
