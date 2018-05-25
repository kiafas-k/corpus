# Corpus

Corpus is an automated corpora builder with NLP capabilities.
Journalists can use it to visualise and monitor sentiment and public opinion about specific topics or entities such as companies or public figures and researchers can use it to build training sets for NLP experimentations. <br>
Corpus can also be used to monitor stock behavior in relevance to significant events. <br>
The longer the parser is on-line the larger the corpora becomes leading to more accurate results.

It is consisted of 2 sub systems:
- Parser
- Webface


### The Parser
The parser is a service that :
- extracts text from user-defined sources
- extracts Named Entities from every article it parses
- estimates the sentiment of the article and classifies it as positive or negative


### The webface
The webface provides a GUI for the user to access and manipulate the data collected by the parser.
It provides 2 things :
- A form with search criteria that allows the user to make a list of articles related to the named entitites the user selects and places them on a timeline along with their sentiment tag.

- Using the same search form the system compiles a trained Naive Bayes classifier for sentiment extraction. It produces a binary file with the pretrained model and provides a download link.



## Installation for Linux

Corpus requires python 3.5 or higher.

- Clone Corpus from github to a folder of your choice (PATH)

- Create a python virtual enironment to that folder

```sh
python3 -m venv <PATH>  

```

- Upgrade the new virtual environment
```sh
<PATH>/bin/python3 -m pip install --upgrade pip setuptools wheel
```

- For easier installation i have included a requirements.txt file which includes all the required libraries.
```sh
<PATH>/bin/python3 -m pip install -r <PATH>/requirements.txt
```


## Create the database
Use the db_structure.sql file to create the database


## Configuration
Each of the two sub systems has a config.ini file in the root folder. 
Modify them according to your setup.



## Usage
### The Parser
The command to execute the parser is :
```sh
<PATH>/bin/python3 <PATH>/parser/parser.py
```
However Parser is not designed to repeat itself or become a memmory resident application. In order to repeat its execution you will need to add the execution command to a scheduled job on your system.

### The webface
The command to execute the webface is :
```sh
<PATH>/bin/python3 <PATH>/webface/server.py
```

Webface uses the Python's HTTPServer library and it serves for ever on port 8000. If you want to stop the server you have to do it manualy.



