import pandas as pd
import dateutil.parser
import datetime
import os
import sys

def percent(num, denom, place=0):
    if denom is 0: return "0%"
    return str(round(int(num)/int(denom) * 100, place))  + "%"

def progress_bar(num, denom):
    progress = int(num/(denom * 3) * 100)
    max_prog = 33
    bar = '\r' + percent(num, denom) + '  |' + '\033[1;32;40m' + '▓' * progress
    print(bar + '\033[0m' + '░' * (max_prog - progress) + '|', end='', flush=True)


def calculate_skipped_heartbeats(file_name, to, num_files):
    data = pd.read_csv(file_name)
    print(data.shape)
    print("Loaded file")
    print("Sorting file")
    data = data.sort_values(["vpr_profile_id", "vpr_session_id", "vpr_timestamp"], ascending = (True, True, False)).reset_index(drop=True)
    print("Done sorting!")
    num_rows = data.shape[0]
    skipped_heartbeats = 0
    affected_sessions_missed = 0
    affected_sessions_late = 0
    affected_sessions_rapid = 0
    prev_timecode = 0
    prev_session = None
    was_heartbeat = False
    prev_time = None
    late_heartbeats = 0
    rapid_heartbeats = 0
    late_minimum = 5
    sessions = pd.DataFrame(columns=['guid', 'video_guid', 'platform', 'platform_details', 'missing_heartbeats', 'heartbeat_gaps', 'late_heartbeats', 'rapid_heartbeats'])
    print("")
    for index, row in data.iterrows():
        if index % int(round(num_rows/num_files)) == 0:
            progress_bar(index, num_rows)
            sessions.to_csv(to + "results" + str(index) + ".csv")
        #heartbeat_interval = int(row['vpr_heartbeat_interval'])
        heartbeat_interval = 30
        timecode = int(row['vpr_timecode'])
        event_type = row['vpr_event_type'] 
        is_heartbeat = event_type == 'heartbeat'
        session = row['vpr_session_id']
        guid = row['vpr_profile_id']
        video_guid = row['vpr_video_guid']
        platform = row['vpr_platform']
        platform_details = row['vpr_platform_details']
        time = dateutil.parser.parse(row['vpr_timestamp'])
        real_time = dateutil.parser.parse(row['vpr_dst'])

        if (session not in sessions.index):
            sessions.loc[session] = [guid, video_guid, platform, platform_details, 0, 0, 0, 0] 
        time = dateutil.parser.parse(row['vpr_local_timestamp'])
        if (is_heartbeat and abs((real_time - time).total_seconds()) > 20):
            rapid_heartbeats += 1
        if (was_heartbeat and is_heartbeat) and (prev_session == session):
            diff_timecode = abs(timecode - prev_timecode)
            diff_localtime = abs((time - prev_time)).total_seconds()
            diff_real_time = abs((real_time - prev_real_time)).total_seconds()
            if (diff_timecode > heartbeat_interval + late_minimum and abs(diff_localtime - diff_timecode) < 15):
                if diff_timecode > heartbeat_interval + late_minimum and diff_timecode < heartbeat_interval + 25:
                    sessions.at[session, 'late_heartbeats'] += 1 
                    late_heartbeats += 1
                else:
                    skip = round(diff_timecode / heartbeat_interval)
                    sessions.at[session, 'missing_heartbeats'] += skip
                    sessions.at[session, 'heartbeat_gaps'] += 1
                    skipped_heartbeats += skip
            if (diff_real_time < 2):
                sessions.at[session, 'rapid_heartbeats'] += 1
                rapid_heartbeats += 1

        prev_time = time
        prev_real_time = real_time
        prev_timecode = timecode
        prev_session = session
        prev_event_type = event_type
        was_heartbeat = is_heartbeat
    num_sessions = sessions.shape[0]
    print(skipped_heartbeats, "heartbeats were skipped total")
    print(late_heartbeats, "heartbeats came in late")
    print(rapid_heartbeats, "heartbeats were rapid")
    total_affected_sessions = 0
    for session_id, row in sessions.iterrows():
        s = False
        if row.loc['missing_heartbeats'] > 0:
            affected_sessions_missed += 1
            s = True
        if row.loc['late_heartbeats'] > 0:
            affected_sessions_late += 1
            s = True
        if row.loc['rapid_heartbeats'] > 0:
            affected_sessions_rapid += 1
            s = True
        if s:
            total_affected_sessions += 1

    print(affected_sessions_missed, "sessions had missing heartbeats", percent(affected_sessions_missed, num_sessions, 2))
    print(affected_sessions_late, "sessions had late heartbeats", percent(affected_sessions_late, num_sessions, 2)) 
    print(affected_sessions_rapid, "sessions had rapid heartbeats", percent(affected_sessions_rapid, num_sessions, 2)) 
    print(num_sessions, "total sessions")
    platforms = {}
    details = {}
    for index, row in sessions.iterrows():
        platform = row['platform']
        detail = row['platform_details']
        if (platform not in platforms):
            platforms[platform] = 0
        if (str(platform + detail) not in details):
            details[platform + detail] = 0

        if (row['missing_heartbeats'] > 0 or row['late_heartbeats'] > 0, row['rapid_heartbeats'] > 0):
            platforms[platform] += 1
            details[platform + detail] += 1
    for key, value in platforms.items():
        print(key, value, percent(value, total_affected_sessions, 2))
    #for key, value in details.items():
    #   print(key, value, percent(value, total_affected_sessions, 2))
    print("Saving to file...")
    sessions.to_csv(to + "results.csv")
    

directory = './data/'
if len(sys.argv) < 4:
    print("Please enter a filename and directory")
    exit()
filename = sys.argv[1]
to = './' + sys.argv[2] + '/'
num_files = int(sys.argv[3])
print("Loading " + to + filename + "...")
calculate_skipped_heartbeats(directory + filename, to, num_files)
