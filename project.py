import pyrebase  #pip install pyrebase4
from flask import Flask, render_template, request #pip install Flask
import time

app = Flask(__name__)

firebaseConfig = {
   "apiKey": "AIzaSyCBdeo2jVFAeu8AqqWI-72YUNmfPmV5GoY",
  "authDomain": "myweb-586c2.firebaseapp.com",
  "databaseURL": "https://my-web-2e75f-default-rtdb.firebaseio.com/",
  "projectId": "myweb-586c2",
  "storageBucket": "myweb-586c2.appspot.com",
  "messagingSenderId": "182370917663",
  "appId": "1:182370917663:web:bb0d914dad7493ddad642a",
  "measurementId": "G-QP2CNGQRBE"
};


firebase = pyrebase.initialize_app(firebaseConfig)
rdb = firebase.database()
sdb = firebase.storage()

count = 0
login_attempts = {}  # Modified data structure

@app.route("/", methods=["GET", "POST"])
def hi():
    global count
    global login_attempts

    if request.form:
        click = request.form["btn"]
        
        if click == "loginbtn":
            return render_template("login.html")
        elif click == "signupbtn":
            return render_template("signup.html")
        elif click == "signupsubmit":
            uname = request.form["username"]
            mail = request.form["email"]
            pwd = request.form["password"]
            mobile = request.form["mobile"]
            img = request.files["profile"]
            
            uname = uname.lower()
            
            details = {
                "name": uname,
                "mail": mail,
                "password": pwd,
                "number": mobile
            }
            
            data = rdb.get().val()
            
            if uname in data:
                return render_template("signup.html", msg="User already exists")
            else:
                rdb.child(uname).update(details)
                sdb.child(uname).put(img)
                return render_template("login.html")

        elif click == "loginsubmit":
            username = request.form["username"].lower()
            password = request.form["password"]

            if username in login_attempts:
                last_attempt_time = login_attempts[username]["time"]
                elapsed_time = time.time() - last_attempt_time

                if elapsed_time < 86400:  # 24 hours in seconds
                    remaining_time = int(86400 - elapsed_time)
                    hours = remaining_time // 3600
                    minutes = (remaining_time % 3600) // 60
                    seconds = remaining_time % 60
                    return render_template("login.html", msg=f"Account blocked. Try again in {hours}h {minutes}m {seconds}s")

                # If 24 hours have passed, remove the user from the block list
                del login_attempts[username]

            dname = rdb.child(username).child("name").get().val()
            dpwd = rdb.child(username).child("password").get().val()

            if( username == dname and password == dpwd):

                return render_template("ish.html", msg="Login successful",pic="static/"+username+".png")
            else:
                count += 1

                if count < 3:
                    return render_template("login.html", msg=f"Wrong credentials. {3 - count} attempts remaining")
                else:
                    # Block the user and store the last attempt time
                    login_attempts[username] = {
                        "attempts": count,
                        "time": time.time()
                    }

                return render_template("home.html", msg="Account blocked. Try again in 24 hours.")

    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True, port=5004)
