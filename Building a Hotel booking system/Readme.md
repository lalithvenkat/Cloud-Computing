# Building a Hotel Booking System

The requirement of this project is to create a web application called room scheduler that  replicates how a general room booking system works where the application will support a multitude 
of rooms and users using python, Google App engine and Flask.

As there is potential for overlap in room bookings, I have also performed a validation to prevent double bookings of rooms.

### Typical requirements and functionality of the application are:
* Login functionality for user, which was achieved with firebase
* Ability to add and delete rooms, restricting the user to add the same room twice nor should a user be able to delete a room that currently has bookings.
* A booking should only be made if it doesn't clash or overlap with other bookings for that room.
* Ability to view all bookings for a given day on a room.
* Ability to delete a booking, But only by that user. 

All these functionalities has been achieved by this application.

## SET-UP
Download/clone the project and run the project by running the main.py program.

Before running install all the required packages by running pip install requirements.txt.

use command python main.py to run this Application.

## CODE FILES AND THEIR PURPOSE:
* Main.py -> A python file where the functionality for the web application is defined. 
* Index.html-> It provides an interface for creating/adding and displaying the rooms.
* edit.html-> A page for modifying bookings for a room in the database 
* Book.html-> This page is for making a booking for a particular room

## Documentation of Methods and functions used:

#### 1) Booking_date_time(start_end)
Here we are registering our function as a Jinja filter by using the @app.template_filter() decorator. Which allows you to change the representation of variables in Jinja templates. This function is used to represent the datetime object for the room bookings. We have used date time object strftime 
that converts the date object to string. We have used to it change the representation of our datetime object for room bookings

#### 2) createUser(claims)
In this function we have defined entity object called user for the datastore, These Entity objects are  used to store a collection of attributes together that belong to one entity. This function will first  generate a key for the user that is linked to the currently logged in user’s email address. The email 
address from this claims object will be used as the identifier for a User entity key. It then attempts to retrieve the user object from the datastore. It checks the datastore by the user key,
• If the entity with corresponding key exists in the datastore then the entity will be retrieved and returned to you.
• If the entity does not exist in the datastore then the entity with corresponding key is added to datastore and datastore will be updated. 

#### 3) retrieveUser(claims)
This Function is responsible for retrieving all the user entity object information.

#### 4) createRoom(room_id)
This function is responsible for creating/adding the rooms. Here we have defined an entity object room for the datastore. We have assigned the room id as the key for the room entity. It then checks 
the datastore for entity with the corresponding key(room id). If the entity is not present(if the room is not present). The entity with that corresponding key will be added to the datastore and updated.

#### 5) deleteRoom(room_id)
This function is similar to the previous one but, here the entity with that key will be deleted from the datastore. Which provides the functionality in deleting the selected room from the app.

#### 6) retrieveRoom(room_id)
This function is responsible for retrieving the specific room.

#### 7) retrieveRooms()
This function retrieves all the rooms of entity kind room. 

#### 8)createBooking(user_email, room_id, start_dt, end_dt)
This function is responsible for creating the room booking. We have passed four parameters for this function such as user email, room_id, start_dt, end_dt. The main functionality here we need is to 
prevent the overlapping of bookings. Lets’s understand the concept here , Suppose if A’s start time is less than or equal B’s end time and B’s start time is less than or equal to A’s end time then A and B 
overlap.

In query 1 we filter to check whether the start time is less than or equal to the end time, similary we check for the same in query2 and the results of the queries are combined. If there is any booking 
present than there is an overlap , else the new booking can be made for that specified time period. 

If the result is none then the entity with the corresponding key will be updated and all its values will 
be updated for that entity in the datastore.

#### 9) updateBooking(booking_id, room_id, start_dt, end_dt)
This function is responsible for updating the booking. This is similar to the previous one but here we retrieve the booking id for the specific room. Again, once we check that there is no overlap of 
booking’s for that room, we can be able to the update the values for this booking.

#### 10) deleteBooking(booking_id)
This function is for deleting the booking for that specific room.

#### 11) retrieveBooking(booking_id)
This function is for retrieving the specific booking for a room in the entity kind booking from the datastore.

#### 12) retrieveBookingsForRoom(room_id)
This function retrieves all the bookings made for the specific room. It queries for the entity kind booking and filters the query by room_id. This function returns all the bookings made for that room 
in a sorting order.

#### 13) retrieveBookings()
This function retrieves all the bookings for the all the rooms from the entity kind booking.

#### 14) searchBooking(start_dt, end_dt)
This function is for querying the datastore for the bookings made for all rooms in a specified time period. We have passed two parameters for this function such as start_date and end_date. Like 
previously we have used two queries for filtering the bookings. we have set the start_date time to 00 hours and the end_date time to 23hrs 59 min for finding the bookings based on the dates. The 
results of both the queries are then combined and displayed.

#### 15) root()
The line of code App.route(“/”) is a flask annotation that specifies that if the host's URL is named with nothing after it, the following method should be used. It's known as root.
Whenever the url is accessed this code is excecuted. This brings up the homepage for sign up and login.When you run this program locally and go to http: / localhost: 8080 /, you'll see the homepage. 

This root () function is called when this annotation is activated. The root () method is set to authenticate the user by importing firebase authentication module. 

This firebase authentication provides the functionality for login and signout. When the user try to login, The root method checks for the token that is obtained from cookies through request and tries to validate it.
If the token is obtained, Then if statement will run and execute the try block. The token is validated using the firebase authentication, If it is valid it records user information to a variable called claims, If not it returns an error_message.

POST method is called in this root() function.POST is a HTTP request method responsible for sending the data in the body of the request. It is used to submitting the data in the form.
Post method is used to create the room from the values given by the user in the form. The createRoom function which was defined earlier is called to create a room. First it checks if the room 
already exists, if it does it prints an error message showing that room already exists, if not creates a new room. My bookings and error forward were passed to the request.args for the query 
parameters to retrieve the information.

Finally this root() function calls the render_template() and render to index.html page with some additional paramaters like userdata, errormessage , error_forward, bookings and also calls the 
retrieveRooms() function that was defined earlier.

#### 16) book(room_id)
Like previously, after validating the user this function is responsible for booking the room. Post method is called in this function to obtain the booking details for the room from the user. Datetime 
object strptime is used to parse the string format of date to datetime object. 

createBooking function that was previously defined is called to check the overlap of bookings for any user. It then calls the retrieveRoom(room_id) and retrieveBookingsForRoom(room_id) functions for retrieving the room 
and bookings for that room while rendering to book.html page along with some additional parameters like user data and error_message.

#### 17) delete(booking_id)
This function is used to delete the booking made for the room. deleteBooking function that was previously defined is called to delete the booking for the room. Booking id for the entity kind 
booking was automatically assigned by google app engine. When the function is called it converts the booking id to int and make it easier to delete the booking for that room and it is redirected to 
homepage.

#### 18) edit(booking_id)
This function is responsible for editing the booking made for a particular room. After validating the user data, Post method is called to obtain the data given by the user in the form. This post method 
collects the data and stores values to the room_id, start and end time variables. It then calls the updateBooking() function that was previously defined which the takes the parameters such as 
room_id, start and end time variables obtained from the post method and passed to this function. This function checks for any overlap with bookings for that room_id and updates the booking.

Finally this function then renders the edit.html page with some additional parameters such as user data, retrieveRoom , retrieveBooking and redirect.

#### 18) remove(room_id)
This function is responsible for deleting the rooms that was created by an user. This function checks if there are any bookings for that particular room by calling the function 
retrieveBookingsForRoom(room_id) that was defined earlier. If there are any bookings for that room it prints an error message showing that the room has bookings in it else it then calls the deleteRoom 
function to delete the room for that particular room_id and it then redirects.

#### 19) query()
This function is responsible for querying the bookings made for all the rooms within a specified time period. The post method is used to collect the start and end time for querying. Datetime object 
strptime parses the string object to date. It then calls the searchBooking() function defined earlier while rendering the index.html page along with some additional parameters such as error message 
and user data.

## Database model
The database here is the datastore, This is a NoSQL database that works on the data by the keyvalue pair.
datastore_client = datastore.Client() This will build a datastore client that will enable us to send 
requests to the datastore to perform CRUD operations.

#### Entity type User
This entity stores the user information with user as a key for this entity. This entity will use email 
address of the user entity for identity the user in the application.

#### Entity type Room
Here the room_id is used as key for identifying the entity type Room. In the request form the entry 
for the datatype is a string.

#### Entity type Booking
Booking is the key for the entity booking and the key is autogenerated by google app engine. The 
booking id is used to identify the bookings for the room.
Booking entity requires the following values for making a booking.
User email: obtained from user entity (presented as a string)
Room_id : obtained from the room entity(presented as a string)
Start_date: date_time object
End_date: date_time objec
