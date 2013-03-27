from flask import Flask
ROOT = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=os.path.join(ROOT, 'public'), static_url_path='/public')
app.config.from_object('config')
app.debug = True

if __name__ == '__main__':
	app.run()