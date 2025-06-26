import datetime
import math 
import pandas as pd


from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Example strategy: 8 minutes run + 2 minutes walk intervals
MARATHON_DISTANCE = 26.2
RUN_MAX = 6
RUN_MIN = 1
BATHROOM_BREAK_TIME = 3
WATER_STOP_TIME = 5

def RaceTimes(hours=0, minutes=0, seconds=0):
    """
    Convert run time from minutes to hours, minutes and seconds.
    """
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)

    result_str = '{:2d}s'.format(seconds)
    if hours > 0 :
        result_str = '{:d}h {:2d}m {:2d}s'.format(hours, minutes, seconds)
    else:
        if minutes > 0 :
            result_str = '{:2d}m {:2d}s'.format(minutes, seconds)
    return result_str
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():

    input_type = request.form.get('input_type')

    if input_type == 'goal':
        goal_hours = int(request.form.get('hours', 0))
        goal_minutes = int(request.form.get('minutes', 0))
        desired_time = RaceTimes(hours=goal_hours, minutes=goal_minutes)
    elif input_type == 'mile_trial':
        mile_min = int(request.form.get('mile_minutes', 0))
        mile_sec = int(request.form.get('mile_seconds', 0))
        mile_time_minutes = mile_min + mile_sec / 60.0

        # Estimate marathon time as 1.3x average mile pace × 26.2 (Jeff Galloway)
        estimated_marathon_minutes = mile_time_minutes * 1.3 * 26.2
        desired_time = RaceTimes(minutes=estimated_marathon_minutes)
    else:
        return "Invalid input type", 400

    print("Desired Marathon Time : ", desired_time)

    # Total time for bathroom breaks and water stops
    break_time = RaceTimes(minutes=BATHROOM_BREAK_TIME + WATER_STOP_TIME)
    desired_time_without_breaks = desired_time - break_time

    # Now compute the average speed needed to achieve this.
    desired_pace = desired_time_without_breaks / MARATHON_DISTANCE
    print("Effective Marathon Pace : ", desired_pace)

    # Fixed walk interval of 30 seconds
    walk_interval = RaceTimes(seconds=30)
    print(walk_interval)

    # Assume that the walking speed is 4 miles per hour or 15 minutes per mile speed
    walk_speed = RaceTimes(minutes=20)

    runStats = []
    for run_interval in [RaceTimes(minutes=j/10) for j in range(10*RUN_MAX, 10*RUN_MIN-1, -5)]:
        num_intervals = desired_time_without_breaks / (run_interval + walk_interval)

        # Divide the intervals into full and partial intervals
        (partial_intervals, full_intervals) = math.modf(num_intervals)
        
        # This is the total time spent running.
        run_time = (full_intervals + partial_intervals) * run_interval
        
        # This is the total time walking
        walk_time = full_intervals * walk_interval
        
        # Distance covered walking
        walk_distance = walk_time / walk_speed
        
        run_distance = MARATHON_DISTANCE - walk_distance
        
        run_speed = run_time / run_distance

        runStats.append({
            "run_interval": run_interval,
            "walk_interval": walk_interval,
            "num_intervals" : num_intervals,
            "run_time" : run_time,
            "run_distance": run_distance,
            "walk_time" : walk_time,
            "walk_distance": walk_distance,
            "run_speed": run_speed,
            "walk_speed": walk_speed
        }) 

    run_df = pd.DataFrame(runStats)

    timeColumns = {
        "run_interval" : "Run Interval",
        "walk_interval" : "Walk Interval",
        "run_time" : "Total Run Time",
        "walk_time" : "Total Walk Time",
        "run_speed" : "Run Speed (min/mile)",
        "walk_speed": "Walk Speed (min/mile)"
    }
    
    result_df = pd.DataFrame()
    for col in timeColumns:
        result_df[timeColumns[col]] = run_df[col].apply(lambda x: format_timedelta(x))

    table_html = result_df.to_html(classes='data', header=True, index=False, table_id="pacing_table")

    # Assumptions
    assumptions = [
        "Total time spent on bathroom breaks: {} minutes".format(BATHROOM_BREAK_TIME),
        "Total time spent at water stops: {} minutes".format(WATER_STOP_TIME)
    ]

    return render_template('calculate.html', 
                           table_html=table_html, 
                           assumptions=assumptions,
                           marathon_time_display=format_timedelta(desired_time),
                           required_pace=format_timedelta(desired_pace))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
