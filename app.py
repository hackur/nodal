from flask import Flask, request, session, redirect, url_for, render_template, flash
import requests, sys, os

app = Flask(__name__)
app.debug = False
app.secret_key = os.environ.get('APP_SECRET_KEY', None)

GITHUB_API_CLIENT_ID = os.environ.get("GITHUB_API_CLIENT_ID", None)
GITHUB_API_CLIENT_SECRET = os.environ.get("GITHUB_API_CLIENT_SECRET", None)

GA_ACCOUNT = os.environ.get("GA_ACCOUNT", None)
GA_DOMAIN_NAME = os.environ.get("GA_DOMAIN_NAME", None)

PROBLEM_LOGGING_IN_ERROR = "There was a problem logging into Nodal. Please try again"
AUTHORIZATION_ERROR = "You must authorize Nodal in order to use it!"

@app.errorhandler(404)
def not_found(error):
	return render_template('error.html'), 404

@app.errorhandler(500)
def error_encountered(error):
	return render_template('error.html'), 500

@app.route('/login', methods=['GET'])
def login():
	return render_template("login.html", client_id=GITHUB_API_CLIENT_ID, ga_account=GA_ACCOUNT, ga_domain_name=GA_DOMAIN_NAME)

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('access_token', None)
	return redirect(url_for('index'))

@app.route("/", methods=['GET'])
def index():
	if 'access_token' in session:
		return render_template("index.html", access_token=session["access_token"], ga_account=GA_ACCOUNT, ga_domain_name=GA_DOMAIN_NAME)
	return redirect(url_for('login'))

@app.route("/without-login", methods=['GET'])
def index_without_login():
	username = request.args.get('username',"");
	return render_template("index.html", access_token="", start_username=username, ga_account=GA_ACCOUNT, ga_domain_name=GA_DOMAIN_NAME)

@app.route('/githubauth', methods=['GET'])
def github_auth():

	error = request.args.get('error',None)
	if error and error == "access_denied":
		flash(AUTHORIZATION_ERROR)
		return redirect(url_for('login'))

	code = request.args.get('code',None)
	if error or (code is None):
		flash(PROBLEM_LOGGING_IN_ERROR)
		return redirect(url_for('login'))

	headers = {
		"Accept": "application/json"
	}

	data = {
		"client_id" : GITHUB_API_CLIENT_ID,
		"client_secret" : GITHUB_API_CLIENT_SECRET,
		"code" : code
	}

	req = requests.post("https://github.com/login/oauth/access_token", headers=headers, data=data, config={"verbose": sys.stdout})

	if req.status_code != 200:
		flash(PROBLEM_LOGGING_IN_ERROR)
		return redirect(url_for('login'))

	access_token = req.json.get("access_token",None)
	if access_token is None:
		flash(PROBLEM_LOGGING_IN_ERROR)
		return redirect(url_for('login'))

	session["access_token"] = access_token

	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(host='0.0.0.0')