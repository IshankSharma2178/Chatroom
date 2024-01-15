import random
from string import ascii_uppercase

from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, join_room, leave_room, send

app=Flask(__name__)
app.secret_key = 'super secret key'
app.config['SECRET_key']="svdbjnljsnlrbgvbjb"
socketio =SocketIO(app)

rooms={}

def generate_unique_code(length):
    while True:
        code=""
        for i in range(length):
            code+= random.choice(ascii_uppercase)
        
        if code not in rooms:
            break

    return code

@app.route("/",methods=["POST","GET"])
def home():
    session.clear()
    if request.method == "POST":
        name=request.form.get("name")
        code=request.form.get("code")
        join=request.form.get("join",False)
        create=request.form.get("create",False)

        if not name:
            return render_template("home.html",error="please enter a name .",code=code,name=name)

        if join !=False and not code:
            return render_template("home.html" , error="please enter a roomcode .",code=code,name=name)

        if create !=False:
            room=generate_unique_code(4)
            rooms[room]={'member':0,'messages':[]}
        elif code not in rooms:
            return render_template("home.html",error="roomcode doesn't exists",code=code,name=name)

        session["room"]=room
        session["name"]=name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    if session.get("room") is None or session.get("name") is None or session.get("room") not in rooms :
        return (url_for("home"))
        
    return render_template("room.html")

@socketio.on("connect")
def connect(auth):
    room=session.get("room")
    name=session.get("name")
    if not room or not name:
        return
    elif room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"name":name,"message":"has entered the room"},to=room)
    rooms[room]["member"]+=1
    print(f"{name} joined room {room}" )


if __name__=="__main__":
    socketio.run(app, debug=True)