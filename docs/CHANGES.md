**Changes from v0.01**
-The bot has been re-written in a much more developer-friendly way
-bot packaged up nicely and moved into coreuptedbot/
-announcmenets are being moved from a file to a db table
-Database migrations. Run the following from v0.01 to get your DB correct
    -```CREATE TABLE announcements(announcement varchar(255);```
    -```CREATE TABLE version (version varchar(255));```
    -```INSERT INTO version values('v0.02');```
    -```CREATE TABLE ignored_users (username varchar(255));```
-create\_db.py has been updated to start you off with a proper database
