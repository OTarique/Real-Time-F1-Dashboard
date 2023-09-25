# Real-time F1 Dashboard

A work in progress real time F1 dashboard that displays scoreboard, race control messages, race updates and other metrics. It uses the live-timing data F1 broadcasts to the SignalR protocol. 

The initial script that communicates with the live-timing SignalR server was taken from [iebb's PixooLiveTiming repo](https://github.com/iebb/PixooLiveTiming). I have edited the script to pull other data and manipulate it as necessary to display on a [streamlit](https://streamlit.io/) dashboard.

Below is video of the dashboard in action:

[video.webm](https://github.com/OTarique/Real-Time-F1-Dashboard/assets/73628289/721d68db-5221-4ce2-b902-a874abe9784f)


I have created a data dictionary that outlines the available endpoints of the live-timing data. This will allow you to adapt the dashboard to your liking. I am still working on finding ways to enrich the information displayed and also making the code cleaner plus efficient to run.
