"""
This is a simple web application that calculates the pacing for a marathon.
"""

import math
import pandas as pd
from pacing_utils import race_times, format_timedelta, milestones

from flask import Flask, request, render_template

app = Flask(__name__)

# Example strategy: 8 minutes run + 2 minutes walk intervals
MARATHON_DISTANCE = 26.2
RUN_MAX = 6
RUN_MIN = 1
BATHROOM_BREAK_TIME = 2
WATER_STOP_TIME = 3
WALK_INTERVAL = race_times(seconds=30)
WALK_SPEED = race_times(minutes=15)

@app.route("/")
def index():
    """
    Render the index page.
    """
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Calculate the pacing for a marathon.
    """
    input_type = request.form.get("input_type")

    # Get walk interval from form or use default
    walk_interval_input = request.form.get("walk_interval")
    if walk_interval_input:
        try:
            walk_interval_seconds = int(walk_interval_input)
            custom_walk_interval = race_times(seconds=walk_interval_seconds)
        except ValueError:
            custom_walk_interval = WALK_INTERVAL
    else:
        custom_walk_interval = WALK_INTERVAL

    if input_type == "goal":
        goal_hours = int(request.form.get("hours") or 0)
        goal_minutes = int(request.form.get("minutes") or 0)
        desired_time = race_times(hours=goal_hours, minutes=goal_minutes)
        magic_mile_pace = desired_time / 1.3 / 26.2
    elif input_type == "mile_trial":
        magic_mile_min = int(request.form.get("mile_minutes") or 0)
        magic_mile_sec = int(request.form.get("mile_seconds") or 0)
        magic_mile_pace = race_times(minutes=magic_mile_min, seconds=magic_mile_sec)
        desired_time = magic_mile_pace * 1.3 * 26.2
    else:
        return "Invalid input type", 400

    # Total time for bathroom breaks and water stops
    desired_pace = desired_time / MARATHON_DISTANCE

    break_time = race_times(minutes=BATHROOM_BREAK_TIME + WATER_STOP_TIME)
    desired_time_without_breaks = desired_time - break_time

    # Now compute the average speed needed to achieve this.
    desired_pace_without_breaks = desired_time_without_breaks / MARATHON_DISTANCE

    run_stats = []
    for run_interval in [
        race_times(minutes=j / 10) for j in range(10 * RUN_MAX, 10 * RUN_MIN - 1, -5)
    ]:
        num_intervals = desired_time_without_breaks / (run_interval + custom_walk_interval)

        # Divide the intervals into full and partial intervals
        (partial_intervals, full_intervals) = math.modf(num_intervals)

        # This is the total time spent running.
        run_time = (full_intervals + partial_intervals) * run_interval

        # This is the total time walking
        walk_time = full_intervals * custom_walk_interval

        # Distance covered walking
        walk_distance = walk_time / WALK_SPEED

        run_distance = MARATHON_DISTANCE - walk_distance

        run_speed = run_time / run_distance

        speed_offset = 100 * (desired_pace_without_breaks - run_speed)/desired_pace_without_breaks

        if speed_offset < 8:
            run_stats.append(
                    {
                    "run_interval": run_interval,
                    "walk_interval": WALK_INTERVAL,
                    "num_intervals": num_intervals,
                    "run_time": run_time,
                    "run_distance": run_distance,
                    "walk_time": walk_time,
                    "walk_distance": walk_distance,
                    "run_speed": run_speed,
                    "walk_speed": WALK_SPEED,
                }
        )

    run_df = pd.DataFrame(run_stats)

    time_columns = {
        "run_interval": "Run Interval",
        "run_speed": "Run Speed (min/mile)",
        "run_time": "Total Run Time",
        "walk_time": "Total Walk Time",
    }

    result_df = pd.DataFrame()
    for col, label in time_columns.items():
        result_df[label] = run_df[col].apply(format_timedelta)

    table_html = result_df.to_html(
        classes="data", header=True, index=False, table_id="pacing_table"
    )

    # Calculate marathon milestones
    milestones_data = milestones(desired_time)
    milestones_df = pd.DataFrame([
        {
            'Milestone': name,
            'Target Time': data['time'],
            'Notes': data['notes']
        }
        for name, data in milestones_data.items()
    ])
    
    milestones_html = milestones_df.to_html(
        classes="data", header=True, index=False, table_id="milestones_table"
    )

    # Calculate training speeds based on Jeff Galloway's method
    training_distances = {
        '5k': 3.1,
        '10k': 6.2,
        'Half Marathon': 13.1,
    }
    training_speeds = []    
    for distance, training_distance in training_distances.items():
        # Jeff Galloway: Training pace is about 30 seconds per mile slower than race pace
        # For shorter distances, the pace difference is smaller
        if distance == '5k':
            training_pace = magic_mile_pace + race_times(seconds=33)
        elif distance == '10k':
            training_pace = magic_mile_pace * 1.15
        elif distance == 'Half Marathon':
            training_pace = magic_mile_pace * 1.2
        else:
            raise ValueError(f"Invalid distance: {distance}")

        target_time = training_pace * training_distance 
        training_speeds.append({
            'Distance': distance,
            'Target Pace': format_timedelta(training_pace),
            'Target Time': format_timedelta(target_time),
        })
    
    training_speeds_df = pd.DataFrame(training_speeds)
    # Transpose the table so distances are rows and pace is the column
    training_speeds_transposed = training_speeds_df.set_index('Distance').T
    training_speeds_html = training_speeds_transposed.to_html(
        classes="data", header=True, index=True, table_id="training_speeds_table"
    )

    # Assumptions
    assumptions = [
        f"Bathroom breaks: {BATHROOM_BREAK_TIME} min, Water stops: {WATER_STOP_TIME} min",
        f"Walk: {format_timedelta(custom_walk_interval)} every interval at {format_timedelta(WALK_SPEED)}/mile",
        f"Run intervals: {RUN_MIN}-{RUN_MAX} min, Distance: {MARATHON_DISTANCE} miles",
        "Strategy: Run-walk intervals for energy conservation"
    ]

    return render_template(
        "calculate.html",
        table_html=table_html,
        milestones_html=milestones_html,
        training_speeds_html=training_speeds_html,
        walk_interval_note=f"Walk Interval = {format_timedelta(custom_walk_interval)} at a speed of {format_timedelta(WALK_SPEED)}/mile",
        assumptions=assumptions,
        marathon_time_display=format_timedelta(desired_time),
        required_pace=format_timedelta(desired_pace),
    )


if __name__ == "__main__":
    app.run()
