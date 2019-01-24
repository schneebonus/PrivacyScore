The current version of the ticketsystem is accessible on https://ps.f5w.de/ticketsystem
For credentials contact me on mark@schneemann.email

Install:

1. Type the following commands to install the python requirenments: 

pip3 install -r requirenments.txt --user
pip3 install -r requirenments-dev.txt --user

2. Change to folder "privacyscore" and create a settings file:

cd privacyscore
cp settings.py.example settings.py

3. Open the settings file and configure your instance:

Search for "set mail credentials here". Fill this section with your e-mail servers credentials.
Search for "set db credentials here". Fill this section with your database servers credentials and host.

4. Add a super-user (back on projects root directory):

cd ..
python3 manage.py createsuperuser <username>
And follow the dialog.

5. Import default data (problemclasses and issue states):
python3 manage.py loaddata ticketsystem

6.1. Start the testserver:

python3 manage.py runserver

You can now use the ticketsystem by opening the following url:
http://127.0.0.1:8000/ticketsystem

Administrative can be done by opening:
http://127.0.0.1:8000/admin

To fetch new e-mails call:
python3 manage.py getemails

To send the daily newsletter / status-mail call:
python3 manage.py dailymail

On a productive system, both commands should be executed by creating cronjobs:
crontab -e
and add rules to execute the commands.

6.2 Mailcrawler
To use the crawler it is required to install:
- Chrome: https://www.google.com/chrome/
- ChromeDriver: http://chromedriver.chromium.org/downloads

The crawler can be used by navigating to crawler/SupportMailCrawler.
To execute it, use the following commands:

For singel scans:
python3 mail-crawler.py 2 --url https://privacyscore.org

To scan a list of url:
python3 mail-crawler.py 3 --list lists/InstitutionsOfHigherEducation.csv
