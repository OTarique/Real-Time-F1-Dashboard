import asyncio
import logging
from signalr_async.net import Hub
from signalr_async.net.client import SignalRClient

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

import merger

logging.basicConfig(level=logging.DEBUG)

st.set_page_config(
    page_title="Real-Time F1 Dashboard",
    page_icon=":car:",
    layout="wide",
)
st.title("Real-Time F1 Dashboard")

placeholder = st.empty()

logging.basicConfig(level=logging.DEBUG)

scoreboard = {}


df_main = pd.DataFrame()

df_info_data = ["Start"]
df_info = pd.DataFrame(df_info_data,columns=["Action"])
df_info = df_info.sort_index(ascending=False)

df_rc = pd.DataFrame()

df_pos = pd.DataFrame(columns=['Action','Position'])

class F1SignalRClient(SignalRClient):
    session_info ={}
    driver_list = {}
    timing_data = {}
    rc_messages = {}
    current_tyres = {}
    lap_count = {}
    weather_data = {}
    track_status = {}
    
    

    def TrackStatus(self,trackStatus):
        merger.merge(self.track_status,trackStatus)

    def CurrentTyres(self,currTyres):
        merger.merge(self.current_tyres,currTyres)

    def RaceControlMessages(self,rcmessages):
        merger.merge(self.rc_messages,rcmessages)
    
    def SessionInfo(self,sessInfo):
        merger.merge(self.session_info,sessInfo)

    def WeatherData(self,weather):
        merger.merge(self.weather_data,weather)

    def DriverList(self, drivers):
        global df_rc
        merger.merge(self.driver_list, drivers)


    def TimingData(self,timing):
        merger.merge(self.timing_data,timing)

        global df_info
        global df_main
        global df_rc
        global df_pos

        


        for driver_number in timing["Lines"]:
            driver = self.driver_list[driver_number]
            driver_timing = self.timing_data["Lines"][driver_number]
            try:
                tyre = self.current_tyres['Tyres'][driver_number]["Compound"]
            except:
                tyre = "-"
            gap = ''
            pos = driver_timing['Position']

            if self.session_info['Type'] == "Qualifying":
                current_part = int(self.timing_data['SessionPart'])
                current_entries = self.timing_data['NoEntries'][current_part - 1]
                if pos == '1':
                    gap = driver_timing['BestLapTimes'][current_part - 1]['Value']
                    pole_data = [driver['LastName']+" is on Pole!"]
                    pole_data_str = driver['LastName']+" is on Pole!"
                    pole_data_test = pole_data_str in df_info['Action'].values
                    if pole_data_test == False:
                        pole_catch = pd.DataFrame(pole_data , columns=["Action"])
                        df_info = pd.concat([df_info,pole_catch], ignore_index=True)
                    
                elif int(pos) > current_entries:
                    gap = 'KO'
                    retired_data = [driver['LastName']+" has been knocked out!"]
                    retired_data_str = driver['LastName']+" has been knocked out!"
                    retired_data_test = retired_data_str in df_info['Action'].values
                    if retired_data_test == False:
                        retired_catch = pd.DataFrame(retired_data , columns=["Action"])
                        df_info = pd.concat([df_info,retired_catch], ignore_index=True)
                elif pos != '1':
                    gap = driver_timing['Stats'][current_part - 1]['TimeDiffToFastest']
                    pos_data = [driver['LastName']+" has moved to position " + pos]
                    pos_data_str = driver['LastName']+" has moved to position " + pos
                    pos_data_test = pos_data_str in df_info['Action'].values
                    if pos_data_test == False:
                        pos_data_catch = pd.DataFrame(pos_data, columns=["Action"])
                        df_info = pd.concat([df_info,pos_data_catch],ignore_index=True)


            elif self.session_info['Type'] == "Practice":
                if 'TimeDiffToFastest' in driver_timing:
                    gap = driver_timing['TimeDiffToFastest']
                if driver_timing['Position'] == '1':
                    gap = driver_timing['BestLapTime']['Value']
                    

            elif self.session_info['Type'] == "Race":
                # position_data = [driver['LastName'] + " in on position " + pos]
                # position_data_str = driver['LastName'] + " in on position " + pos
                # position_test = position_data_str in df_pos['Action'].values
                position_data_driver = driver['LastName']
                position_data = [[position_data_driver, pos]]
                position_data_test = position_data_driver in df_pos['Action'].values

                if position_data_test == False:
                    position_catch = pd.DataFrame(position_data, columns=["Action","Position"])
                    df_pos = pd.concat([df_pos,position_catch],ignore_index=True)
                
                elif int(df_pos.loc[df_pos['Action'] == position_data_driver]['Position'].values[0]) < int(pos):
                    for driverno in self.timing_data['Lines']:
                        if self.timing_data["Lines"][driverno]['Position'] == str(int(pos)-1):
                            p_driver = self.driver_list[driverno]['LastName']
                            break
                        else:
                            p_driver = ""
                    
                    pos_data = [driver['LastName'] + " has overtaken position " + str(int(pos)-1) + " " + p_driver]
                    pos_data_catch = pd.DataFrame(pos_data, columns=["Action"])
                    df_info = pd.concat([df_info,pos_data_catch],ignore_index=True)
                    df_pos[position_data_driver]['Position'] = pos

                InPit = driver_timing['InPit']
                if driver_timing['GapToLeader'] == "" and InPit != True:  # race
                    gap = "OUT"
                    retired_data = [driver['Tla']+" is OUT!"]
                    retired_catch = pd.DataFrame(retired_data , columns=["Action"])
                    df_info = pd.concat([df_info,retired_catch], ignore_index=True)
                    
                else:
                    gap = driver_timing['GapToLeader']

                
                if InPit == True:
                    action_pit_data = [driver['LastName']+" is in Pit"]
                    action_pit_str = driver['LastName']+" is in Pit"
                    action_test = action_pit_str in df_info['Action'].values
                    if action_test == False:    
                        action_pit = pd.DataFrame(action_pit_data,columns={"Action"})
                        df_info = pd.concat([df_info,action_pit], ignore_index=True)
                #     df_prev.loc[int(pos),'InPit'] = True
                # else:
                #     df_prev.loc[int(pos),'InPit'] = False


                IntervalGap = driver_timing['IntervalToPositionAhead']['Value']
                catching = driver_timing['IntervalToPositionAhead']['Catching']
                if catching == True:
                    for driverno in self.timing_data['Lines']:
                        if self.timing_data["Lines"][driverno]['Position'] == str(int(pos)-1):
                            c_driver = self.driver_list[driverno]['LastName']
                            break
                        else:
                            c_driver = ""
                    action_catch_data = [driver['LastName']+" is catching position "+str(int(pos)-1)+" "+c_driver]
                    action_catch_str = driver['LastName']+" is catching position "+str(int(pos)-1)+" "+c_driver
                    action_test = action_catch_str in df_info['Action'].values
                    if action_test == False:
                        action_catch = pd.DataFrame(action_catch_data, columns=["Action"])
                        df_info = pd.concat([df_info,action_catch], ignore_index=True)
                #     df_prev.loc[int(pos),'Catching'] = True
                # else:
                #     df_prev.loc[int(pos),'Catching'] = False

                    


                if 'NumberOfPitStops' in driver_timing:
                    NumberOfPitStops = driver_timing['NumberOfPitStops']
                else:
                    NumberOfPitStops = 0

                if 'BestLapTime' in driver_timing:
                    if driver_timing['BestLapTime']['Value'] == "":
                        BestLapTime = "9:00.000"
                    else:

                        BestLapTime= driver_timing['BestLapTime']['Value']
                else:
                    BestLapTime="9:00.000"
            
            # df_prev.loc[int(pos), 'Position'] = pos


            if self.session_info['Type'] == "Race":
                scoreboard[driver_number] = {
                "Position": pos,
                "Driver": driver['Tla'],
                "Gap": gap,
                "Interval": IntervalGap,
                "Catching" : catching,
                "In Pit": InPit,
                "Pit Stops":NumberOfPitStops,
                "Tyre" : tyre,
                "BestLapTime" : BestLapTime
            }

            else:
                scoreboard[driver_number] = {
                    "Position": pos,
                    "Driver": driver['Tla'],
                    "Gap": gap,
                    "Tyre" : tyre,
                }

            df_main = pd.DataFrame(scoreboard)
            df_main = df_main.transpose()
            df_main['Position'] = df_main['Position'].astype(int)
            if self.session_info['Type'] == 'Race':
                df_main['BestLapTime'] = df_main['BestLapTime'].apply(pd.to_datetime, format='%M:%S.%f').dt.time
                FastestLapDriverNo = df_main.loc[df_main['BestLapTime'] == df_main['BestLapTime'].min()].index[0]
                FastestLapDriverName = self.driver_list[FastestLapDriverNo]['Tla']
                FastestLapTime = df_main.loc[df_main['BestLapTime'] == df_main['BestLapTime'].min()]['BestLapTime'].values[0]
            else:
                FastestLapDriverNo = "-"
                FastestLapDriverName = "-"
                FastestLapTime = "-"
            df_main.sort_values(by=['Position'], inplace=True)

            df_info = df_info.sort_index(ascending=False)

            df_rc = pd.DataFrame(self.rc_messages['Messages'])
            df_rc = df_rc.sort_index(ascending=False)

            if 'Message' in self.track_status:
                track_status = self.track_status['Message']
            else:
                track_status = "-"

            airtemp = self.weather_data['AirTemp']
            tracktemp = self.weather_data['TrackTemp']
            windspeed = self.weather_data['WindSpeed']



        with placeholder.container():
            st.subheader(self.session_info['Type']+" - "+self.session_info['Meeting']['Name'])
            col1,col2 = st.columns([0.45,0.5])
            with col1:
                
                st.metric('Fastest Lap',str(FastestLapDriverName) + " - " + str(FastestLapTime))

                st.subheader('Race Details', divider='red')
                st.dataframe(df_main, use_container_width=True,column_config={"BestLapTime":None})

            with col2:
                c1,c2,c3, c4 = st.columns([0.4,0.2,0.2,0.2])
                c1.metric('Track status',track_status)
                c2.metric('Air Temp',airtemp)
                c3.metric('Track Temp',tracktemp)
                c4.metric('Wind Speed',windspeed)
                
                st.subheader('Actions', divider='blue')
                st.dataframe(df_info, height=150, use_container_width=True)

                st.subheader('Radio Control Messages', divider='green')
                st.dataframe(df_rc,height = 150, use_container_width=True)

    async def _process_message(self, message):
        if hasattr(message, "result"):
            print(message)
            for k in message.result:
                print(k)
                if hasattr(self, k):
                    getattr(self, k)(message.result[k])
                else:
                    print(k, message.result[k])
        elif hasattr(message, "arguments"):
            k, v, t = message.arguments
            if hasattr(self, k):
                getattr(self, k)(v)
            else:
                print(k, v)


_connection_url = 'https://livetiming.formula1.com/signalr'
hub = Hub("streaming")

   

async def run_client():
    async with F1SignalRClient(
            _connection_url,
            [hub],
            keepalive_interval=5,
    ) as client:
        await hub.invoke("Subscribe", [
                        "TrackStatus",
                        "CurrentTyres",
                        "RaceControlMessages",
                       "SessionInfo",
                       "WeatherData",
                       "DriverList",
                       "TimingData",

])
        await client.wait(timeout=5)


async def main():
    await asyncio.gather(
        run_client()
    )


if __name__ == "__main__":
    asyncio.run(main())