# Poem-Finder

## Introduction

This repository contains most of the necessary files to run the "Poem-Finder" search engine. However, the program ***runs exclusively on Elasticsearch***. As such, you must install Elasticsearch before launching the engine. The steps to properly install and run the engine are writen below.

## Installing and Preconfiguring Elasticsearch

1. Download Elasticsearch [here](https://www.elastic.co/downloads/elasticsearch). It should bring you to this page: </br></br>
![demo 1](/instruction_img/1.jpg)</br></br>
2. Select "Choose platform" dropdown to choose your compatible operating system.
3. Click the blue button to download Elasticsearch
4. After it finished downloading, extract the folder. Then in the folder path `\bin\`. Click open the file `elasticsearch.bat` and run the program.
</br></br>![demo 2](/instruction_img/2.jpg)</br></br>
6. A command prompt should pop up after this. Wait for around 3 minutes until the commands appear to stop running, then close the program.
7. Next, in the folder path `\config\`. Click open the file `elasticsearch.yml` in any text/code editor.
</br></br>![demo 3](/instruction_img/3.jpg)</br></br>
8. On lines 92 and 94 replace the values of `true` to `false` then save and close the editor.
</br></br>![demo 4](/instruction_img/4.jpg)</br></br>

## Running the Search Engine

1. Ensure that the virtual environment used for running python programs has the modules `elasticsearch`, `flask`, and `flask-cors` installed.
2. In the `elasticsearch-X.X.X` folder path `\bin\`. Click open the file `elasticsearch.bat` and run the program.
3. Then, in the `backend` folder, run `api_server.py`
