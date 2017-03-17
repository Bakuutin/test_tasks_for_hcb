# Original Task

Write a web application which:

- Allows to select once any number in the range from 1 to 10
- Displays the sum of all selected numbers in real time
- Easily scales for a large number of users

#### Required endpoints

- `/session`  Creates a new session, returns the token
- `/vote` Here comes the numbers. Requires the token
- `/online` Web socket, streams current sum

# How To Deploy

    pip install -Ur requirements.txt
    npm install
    bower install
    python3.6 server.py
