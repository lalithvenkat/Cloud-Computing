import uuid
from datetime import datetime, timedelta
from os import environ

from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token

firebase_request_adapter = requests.Request()

environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"

datastore_client = datastore.Client()

app = Flask(__name__)


@app.template_filter()
def booking_date_time(start_end):
    start = start_end[0]
    end = start_end[1]

    if start.date() == end.date():
        return [start.strftime("%d %b, %Y"), start.strftime("%I: %M %p") + " - " + end.strftime("%I: %M %p")]

    else:
        return [start.strftime("%d %b, %Y %I: %M %p -"), end.strftime("%d %b, %Y %I: %M %p")]


def createUser(claims):
    entity_key = datastore_client.key("User", claims.get("email"))
    if (datastore_client.get(entity_key)):
        return False

    entity = datastore.Entity(key=entity_key)
    entity.update({
    })
    datastore_client.put(entity)
    return True


def retrieveUser(claims):
    entity_key = datastore_client.key("User", claims.get("email"))
    return datastore_client.get(entity_key)


def createRoom(room_id):
    entity_key = datastore_client.key("Room", room_id)
    if datastore_client.get(entity_key) is not None:
        return False

    entity = datastore.Entity(key=entity_key)
    entity.update({
    })
    datastore_client.put(entity)
    return True


def deleteRoom(room_id):
    entity_key = datastore_client.key("Room", room_id)
    datastore_client.delete(entity_key)
    return True


def retrieveRoom(room_id):
    entity_key = datastore_client.key("Room", room_id)
    return datastore_client.get(entity_key)


def retrieveRooms():
    query = datastore_client.query(kind="Room")
    return [x for x in query.fetch()]


def createBooking(user_email, room_id, start_dt, end_dt):
    query1 = datastore_client.query(kind="Booking")
    query1.add_filter("room", "=", room_id)
    query1.add_filter("start", "<=", end_dt - timedelta(0, 59))
    result1 = [entity.key.id for entity in query1.fetch()]

    query2 = datastore_client.query(kind="Booking")
    query2.add_filter("room", "=", room_id)
    query2.add_filter("end", ">=", start_dt + timedelta(0, 59))
    result2 = [entity for entity in query2.fetch()]

    result = [entity for entity in result2 if entity.key.id in result1]

    if result:
        return False

    entity_key = datastore_client.key("Booking")
    entity = datastore.Entity(key=entity_key)
    entity.update({
        "user": user_email,
        "room": room_id,
        "start": start_dt,
        "end": end_dt
    })
    datastore_client.put(entity)
    return True


def updateBooking(booking_id, room_id, start_dt, end_dt):
    booking = retrieveBooking(booking_id)
    print(booking.key.id)
    query1 = datastore_client.query(kind="Booking")
    query1.add_filter("room", "=", room_id)
    query1.add_filter("start", "<=", end_dt - timedelta(0, 59))
    result1 = [entity.key.id for entity in query1.fetch()]

    for x in result1:
        print("R1", x)
    try:
        result1.remove(booking.key.id)
    except:
        pass

    for x in result1:
        print("R1-", x)

    query2 = datastore_client.query(kind="Booking")
    query2.add_filter("room", "=", room_id)
    query2.add_filter("end", ">=", start_dt + timedelta(0, 59))
    result2 = [entity for entity in query2.fetch()]

    for x in result2:
        print("R2", x)
    try:
        result2.remove(booking)
    except:
        pass

    for x in result2:
        print("R2-", x)

    result = [entity for entity in result2 if entity.key.id in result1]

    if result:
        return False

    booking.update({
        "room": room_id,
        "start": start_dt,
        "end": end_dt
    })
    datastore_client.put(booking)
    return True


def deleteBooking(booking_id):
    entity_key = datastore_client.key("Booking", booking_id)
    datastore_client.delete(entity_key)
    return True


def retrieveBooking(booking_id):
    entity_key = datastore_client.key("Booking", booking_id)
    return datastore_client.get(entity_key)


def retrieveBookingsForRoom(room_id):
    query = datastore_client.query(kind="Booking")
    query.add_filter("room", "=", room_id)
    query.add_filter("start", ">", datetime(1970, 1, 1))  # keeps sorting order to start date/time
    return [x for x in query.fetch()]


def retrieveBookings():
    query = datastore_client.query(kind="Booking")
    return [x for x in query.fetch()]


def searchBooking(start_dt, end_dt):
    print(start_dt, end_dt)
    query1 = datastore_client.query(kind="Booking")
    end_dt = end_dt.replace(hour=23, minute=59, second=59)
    query1.add_filter("start", "<=", end_dt)
    result1 = [entity.key.id for entity in query1.fetch()]

    print("%%%%%%%%%")
    for x in result1:
        print("1", x)

    query2 = datastore_client.query(kind="Booking")
    start_dt = start_dt.replace(hour=0, minute=0, second=0)
    query2.add_filter("end", ">=", start_dt)
    result2 = [entity for entity in query2.fetch()]

    print("$$$$$$$$$")
    for x in result2:
        print(2, x)

    result = [entity for entity in result2 if entity.key.id in result1]

    print("@@@@@@@@@@")
    for x in result:
        print(3, x)

    return result


@app.route("/", methods=["GET", "POST"])
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    bookings = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    if request.method == "POST":
        if not createRoom(request.form["room_id_new"]):
            error_message = "Room with id {} exists".format(request.form['room_id_new'])
        else:
            error_message = "Room with id {} added successfully".format(request.form['room_id_new'])

    if "mybookings" in request.args:
        bookings = retrieveBookings()

    error_forward = None
    if "error_forward" in request.args:
        error_forward = request.args["error_forward"]

    return render_template("index.html", user_data=claims, error_message=error_message, rooms=retrieveRooms(),
                           bookings=bookings, error_forward=error_forward)


@app.route("/book/<room_id>", methods=["GET", "POST"])
def book(room_id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    unhide = False
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    if request.method == "POST":
        start = datetime.strptime(request.form["booking_start_date_new"]
                                  + " "
                                  + request.form["booking_start_time_new"],
                                  "%Y-%m-%d %H:%M")
        end = datetime.strptime(request.form["booking_end_date_new"]
                                + " "
                                + request.form["booking_end_time_new"],
                                "%Y-%m-%d %H:%M")

        if start >= end:
            error_message = "Start can not be after or same as End"
        elif start < datetime.now():
            error_message = "Start can not be in the past"
        elif not createBooking(claims.get("email"), room_id, start, end):
            error_message = "Start and End overlaps another booking"
        else:
            error_message = "Room booked successfully"

    if "unhide" in request.args:
        unhide = True

    error_forward = None
    if "error_forward" in request.args:
        error_forward = request.args["error_forward"]

    return render_template("book.html", user_data=claims, error_message=error_message, room=retrieveRoom(room_id),
                           bookings=retrieveBookingsForRoom(room_id), unhide=unhide, error_forward=error_forward)


@app.route("/delete/<booking_id>", methods=["GET", "POST"])
def delete(booking_id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    unhide = False
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    deleteBooking(int(booking_id))
    return redirect(request.args["redirect"])


@app.route("/edit/<booking_id>", methods=["GET", "POST"])
def edit(booking_id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    unhide = False
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    if request.method == "POST":
        room_id = request.form["booking_room_new"]
        start = datetime.strptime(request.form["booking_start_date_new"]
                                  + " "
                                  + request.form["booking_start_time_new"],
                                  "%Y-%m-%d %H:%M")
        end = datetime.strptime(request.form["booking_end_date_new"]
                                + " "
                                + request.form["booking_end_time_new"],
                                "%Y-%m-%d %H:%M")

        if start >= end:
            error_message = "Start can not be after or same as End"
        elif start < datetime.now():
            error_message = "Start can not be in the past"
        elif not updateBooking(int(booking_id), room_id, start, end):
            error_message = "Start and End overlaps another booking"
        else:
            error_message = "Booking updated successfully"
            if "?" in request.args["redirect"]:
                return redirect(request.args["redirect"] + "&error_forward=" + error_message)
            else:
                return redirect(request.args["redirect"] + "?error_forward=" + error_message)

    return render_template("edit.html", user_data=claims, error_message=error_message,
                           booking=retrieveBooking(int(booking_id)), rooms=retrieveRooms(),
                           redirect=request.args["redirect"])


@app.route("/remove/<room_id>", methods=["GET", "POST"])
def remove(room_id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    unhide = False
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    if retrieveBookingsForRoom(room_id):
        error_message = "Room {} has bookings in it".format(room_id)
    else:
        deleteRoom(room_id)
        error_message = "Room {} deleted successfully".format(room_id)
    return redirect("/?error_forward=" + error_message)


@app.route("/query", methods=["GET", "POST"])
def query():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    bookings = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    if request.method == "POST":
        start = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end = datetime.strptime(request.form["end_date"], "%Y-%m-%d")

        if start > end:
            return redirect("/?error_forward=Start after end date?")

        return render_template("index.html", user_data=claims, error_message=error_message,
                               search=searchBooking(start, end))


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
