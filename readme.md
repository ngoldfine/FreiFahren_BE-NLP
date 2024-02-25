# Freifahren

## What is Freifahren?
Freifahren is a project that aims to track all ticket inspectors in the berlin public transport system. The goal is to provide a live map of all ticket inspectors in the city, so that people can avoid them for whatever reason.

The data for the live map is provided by the community of the [Freifahren](https://t.me/freifahren_BE) Telegram group. Members of the group are reporting when they see ticket inspectors and the data is then processed and displayed on the map. This repository is responsible for the natural language processing and the data processing of the messages in the Telegram group.

## Quickstart Guide

### Prerequisites
- Python 3.6 or higher

### Setup
1. Clone the repository
````bash
git clone https://github.com/johan-t/freiFahren
````
2. Install the required packages with `pip install -r requirements.txt`
3. Set the environment variable `BOT_TOKEN` to your Bot API Token. You can get one by creating a new bot with the [BotFather](https://t.me/botfather).

### Run the bot
````bash
python main.py
````
Once the bot is running it will start processing the messages it receives from the Telegram group.

## How does it work?
When the bot notices a new message in the group it will trigger the `extract_data` function. This function will extract the relevant information of station where the ticket inspectors were seen, the name of line they were on, the direction the train was going as well as the time of the sighting. 


