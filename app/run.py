#author : eric mourgya
#
import commands
from flask import jsonify
from flask import  Flask, Response, request, redirect,session, url_for
from flask.ext.login import LoginManager, UserMixin,login_required, login_user, logout_user
#@app.after_request
#def treat_as_plain_text(response):
#    response.headers["content-type"] = "text/plain; charset=utf-8"
#    return response


app = Flask(__name__)
app.secret_key="gloubiboulga"
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"



class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)



@app.route('/', methods = ['GET'])
@login_required
def help():
    """Welcome page and help page."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

def cmdline(cmd):
        #  make and exec of  cmd command on system
        status, output = commands.getstatusoutput(cmd)
        if status != 0:
                error_str= cmd + ": command failed! : " +status+" "+output
                print error_str
                return error_str
        else:
                print cmd + "done"
                return output


@app.route('/show/discovery')
@login_required
def showdiscovery():
    	"""------------------------Show discovery portals."""
	cmdshow="iscsiadm -m discovery -P1"
	res=cmdline(cmdshow)
	return Response(response=res,status=200,mimetype="text/plain")


@app.route('/show/nodes')
@login_required
def shownodes():
    	"""Show nodes."""
	cmdshow="iscsiadm -m node -P1"
	res=cmdline(cmdshow)
	return Response(response=res,status=200,mimetype="text/plain")



@app.route('/show/disks')
@login_required
def showdisk():
    	"""Show discovery disk."""
	cmdshow="iscsiadm -m session -P3"
	res=cmdline(cmdshow)
	return Response(response=res,status=200,mimetype="text/plain") 


@app.route('/show/lsblk')
@login_required
def showlsblk():
    	"""Show discovery sessions and  disks."""
	cmdshow="lsblk"
	res=cmdline(cmdshow)
	return Response(response=res,status=200,mimetype="text/plain")


@app.route('/show/sessiondetail')
@login_required
def showsessiondetail():
    	"""Show session in  detail without disk."""
	cmdshow="iscsiadm -m session -P1"
	res=cmdline(cmdshow)
	return Response(response=res,status=200,mimetype="text/plain") 

@app.route('/show/session')
@login_required
def showsession():
    	"""Show session ids"""
	cmdshow="iscsiadm -m session"
	res=cmdline(cmdshow)

	return Response(response=res,status=200,mimetype="text/plain") 


@app.route('/show/specifiquesession',methods=["GET", "POST"])
@login_required
def showspecifiquesession():
    """show  specifique  session"""
    if request.method == 'POST':
        session=request.form['session']
        cmdres="iscsiadm -m session -r"+session +" -P3"
        res=cmdline(cmdres)
        return Response(response=res,status=200,mimetype="text/plain")
    else:
        return Response('''
        <form action="" method="post">
            <p><input placeholder="session id" type=text name=session>
            <p><input type=submit value=submit>
        </form>
        ''')
         

@app.route('/rescan/session',methods=["GET", "POST"])
@login_required
def rescansession():
    """rescan a  specifique  session"""
    if request.method == 'POST':
        ip=request.form['session']
        
        cmdres="iscsiadm -m session -r"+session +" -R"
        res=cmdline(cmdres)
        return redirect(url_for('showspecifiquesession'),code=302)
    else:
        return Response('''
        <form action="" method="post">
            <p><input placeholder="session id" type=text name=session>
            <p><input type=submit value=submit>
        </form>
        ''')



@app.route('/make/discovery',methods=["GET", "POST"])
@login_required
def makediscovery():
    """make a discovery
    """
    if request.method == 'POST':
        ipaddr=request.form['ip']
        print ipaddr
        cmdres="iscsiadm -m discovery -t sendtargets -p "+ipaddr+":3260 -P 1"
        res=cmdline(cmdres)
        return Response(response=res,status=200,mimetype="text/plain")
    else:
        return Response('''
        <form action="" method="post">
            <p><input placeholder="portal ip" type=text name=ip>
            <p><input type=submit value=submit>
        </form>
        ''')
         


@app.route('/make/nodelogin',methods=["GET", "POST"])
@login_required
def makenodelogin():
    """make a node login
    """
    if request.method == 'POST':
        ipaddr=request.form['ip']
        iqn=request.form['iqn']
        cmdres="iscsiadm -m node "+ iqn + "-p " +ipaddr + "-o update -n node.startup -v automatic"
        res=cmdline(cmdres)
        return Response(response=res,status=200,mimetype="text/plain")
    else:
        return Response('''
        <form action="" method="post">
            <p><input placeholder="portal ip" type=text name=ip>
            <p><input placeholder="portal iqn" type=text name=iqn>
            <p><input type=submit value=submit>
        </form>
        ''') 
 

@app.route('/make/sessionlogin',methods=["GET", "POST"])
@login_required
def makesessionlogin():
    """make a session login
    """
    if request.method == 'POST':
        ipaddr=request.form['ip']
        iqn=request.form['iqn']
        cmdres="iscsiadm -m node "+ iqn + "-p " +ipaddr + "-l"
        res=cmdline(cmdres)
        return Response(response=res,status=200,mimetype="text/plain")
    else:
        return Response('''
        <form action="" method="post">
            <p><input placeholder="portal ip" type=text name=ip>
            <p><input placeholder="portal iqn" type=text name=iqn>
            <p><input type=submit value=submit>
        </form>
        ''') 


@app.route("/login", methods=["GET", "POST"])
def login():
    """login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[0]
            user = User(id)
            login_user(user)
            return redirect(url_for('help'))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input placeholder="Username"  type=text name=username>
            <p><input placeholder="Password" type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')

@app.route("/logout")
@login_required
def logout():
    """logout page """
    logout_user()
    return Response('<p>Logged out</p>')


@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')



@login_manager.user_loader
def load_user(userid):
    return User(userid)


app.run(debug=True,port=5001)
