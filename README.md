# Ticks Up
Read more about this project at

https://docs.google.com/document/d/1pQ-CcS6LQffKXhaLbfQu2N_Hnn0jDHf4YlEQg1eRbAY/edit?usp=sharing
## Getting started
First, download the repo using:
````
git pull https://github.com/chaiwanlin/TicksUp.git
````
Then to checkout our latest milestone:
````
git checkout milestone1
````
Next, you will have to install the requirements for the app to run.
Make sure you are in the main directory.
````
pip install -r requirements.txt
````
You are now ready to launch our website.
Change into the `ticks_up` directory and follow the following commands:
````
cd ticks_up
python manage.py migrate
python manage.py runserver
````
Now open a browser and go to http://localhost:8000/dashboard/.

**Have fun exploring!**
