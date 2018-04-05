
SmartMirror
===========

SmartMirror is an intelligent home application designed to provide information on
mirror's surface, this can be achieved by placing a screen behind a two way mirror.
Currently working under windows, will be ported to work with raspberry pi using 
it's camera module.
Documentation can be found here: [**docs**](https://bbialoskorski.github.io/SmartMirror/index.html).

Features:
---------
- Current time and date information
- Current weather information
- Upcoming Google calendar events
- Personalized 'Hello' messages
- Edit mode (user decides widget placement)
- Face detection and recognition
  - Face recognition triggers display of according 'Hello' message/calendar 

Requires:
---------
- Python 3.3+
- Modules:
	- OpenCV 3.x
	- opencv_contrib
	- NumPy
	- PIL
	- requests
	- google_auth_oauthlib
	- googleapiclient
- Camera

How to use it?
-------------
1. Clone this repository with `$ git clone https://github.com/bbialoskorski/SmartMirror`
2. Run \_\_main__.py

The first thing you'll see is this **menu** page:

![](https://i.imgur.com/UAtIVD8.png)

Let's look at avaible options from top to bottom.

>![](https://i.imgur.com/B1wQ1UQ.png)
>
> This page allows user to collect face photos and use them to train the recognizer. 
> Enter a name and click 'Collect training data'. Camera feed will appear and 30 photos
> will be snapped and cropped to detected face region. While collecting data only one
> person should be standing in front of a mirror in a regular distance. While photos are 
> being taken it's okay to move your head around slightly but without rapid movements.
> After that camera feed will disappear and train button will become avaible. If anything
> went wrong you can reset collected data by pressing 'Reset' button or by going back
> to the main menu. Once you click 'Train' face recognizer will be trained with collected
> data and your name and face will be saved in the application.

>![](https://i.imgur.com/AQyOGGA.png)
>
> This page can be used to log in to Google Calendar. Because Calendar is displayed
> only when face is recognized this option is avaible only to users who 'registered' with
> the recognizer. Note that you have to log in and authorize calendar each time you open
>  SmartMirror application. When you click 'Authenticate Calendar' your browser will
>  open on google's authentication page. Once you log in you have to give this application
>  read permissions. If you want to stop authentication process simply click 'Cancel'.

> Once you've finished setting up your application press 'Start SmartMirror'. 

Once it's started this is what you'll see:
![](https://i.imgur.com/4uh4Wd1.png)
> By pressing **Tab** you can enter/exit edit mode. While in edit mode you can move
> around your widgets by dragging them with your mouse cursor while holding left
> mouse button (new positions will be saved). You will recognize edit mode by yellow
> borders surrounding each widget (sample message and calendars events are also 
> displayed).
![](https://i.imgur.com/Acw3xlY.png)

# To properly close the application from this screen press ESC button.