# CIS-400-Team-Project

## Website
https://twitterdataelectionpredictor.herokuapp.com/

## Github
https://github.com/T-Boya/CIS-400-Team-Project/tree/Tinashe-Osewe

## Installation Instructions
Run pip install -r requirements.txt to install required dependencies

## Startup Instructions
<ol>
<li>Navigate to root directory</li>
<li>Run 'python manage.py runserver'</li>
<li>Navigate to url given in console (likely http://127.0.0.1:8000/)</li>
</ol>

## Using the website
### Live Search
Click on 'Live Search' in navigation bar or at bottom of page to analyzy live twitter data.

### Archive Search
Click on 'Archive Search' in the navigation bar or at the bottom of the page then select a date range to analyze past twitter data.

## Relevant Files
The following files are relevant to this course:
<ol>
<li>prediction/sentiment_analysis.py</li>
<li>prediction/live_data_analyzer.py</li>
<li>prediction/views.py</li>
</ol>
The remainder are necessary only for the running of the website and due to their large number have not been commented (as it is unusual
to comment dependencies and similar types of files)

## Notes
Running the program on heroku may lead to an application error. This is not because of an error within the program but because heroku terminates all non asynchronous requests that run for over thirty seconds. This issue will not come up when running the program on localhost. A common issue with python localhost however is that if it is left inactive for a long time it may freeze without giving feedback and pages will load forever, this can be fixed by stopping (cntl + c) and restarting it.