# Flight Recommendation REST Api

Sitting on top of the Amadeus flight API, creates custom recommendations based on travel history, and uses either submission of text or images to improve recommendations - utilising BeautifulSoup to webscrape to create a database of options.

This is built with Flask, Flask-RESTful, Flask-JWT, and Flask-SQLAlchemy.

Deployed on AWS using UWSGI for concurrency and auto-reboot.


