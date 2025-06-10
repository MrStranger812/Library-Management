from factory import create_app
from config import Config

def get_app(config_class=Config):
    return create_app(config_class)

if __name__ == '__main__':
    app = get_app()
    app.run(debug=True)

