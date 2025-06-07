from factory import create_app

def get_app(config=None):
    return create_app(config)

if __name__ == '__main__':
    app = get_app()
    app.run(debug=True)

