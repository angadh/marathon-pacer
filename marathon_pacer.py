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
BATHROOM_BREAK_TIME = 3
WATER_STOP_TIME = 5
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

    if input_type == "goal":
        goal_hours = int(request.form.get("hours", 0))
        goal_minutes = int(request.form.get("minutes", 0))
        desired_time = race_times(hours=goal_hours, minutes=goal_minutes)
    elif input_type == "mile_trial":
        mile_min = int(request.form.get("mile_minutes", 0))
        mile_sec = int(request.form.get("mile_seconds", 0))
        mile_time_minutes = mile_min + mile_sec / 60.0

        # Estimate marathon time as 1.3x average mile pace × 26.2 (Jeff Galloway)
        estimated_marathon_minutes = mile_time_minutes * 1.3 * 26.2
        desired_time = race_times(minutes=estimated_marathon_minutes)
    else:
        return "Invalid input type", 400

    # Total time for bathroom breaks and water stops
    break_time = race_times(minutes=BATHROOM_BREAK_TIME + WATER_STOP_TIME)
    desired_time_without_breaks = desired_time - break_time

    # Now compute the average speed needed to achieve this.
    desired_pace = desired_time_without_breaks / MARATHON_DISTANCE

    run_stats = []
    for run_interval in [
        race_times(minutes=j / 10) for j in range(10 * RUN_MAX, 10 * RUN_MIN - 1, -5)
    ]:
        num_intervals = desired_time_without_breaks / (run_interval + WALK_INTERVAL)

        # Divide the intervals into full and partial intervals
        (partial_intervals, full_intervals) = math.modf(num_intervals)

        # This is the total time spent running.
        run_time = (full_intervals + partial_intervals) * run_interval

        # This is the total time walking
        walk_time = full_intervals * WALK_INTERVAL

        # Distance covered walking
        walk_distance = walk_time / WALK_SPEED

        run_distance = MARATHON_DISTANCE - walk_distance

        run_speed = run_time / run_distance

        speed_offset = 100 * (desired_pace - run_speed)/desired_pace

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
        "run_time": "Total Run Time",
        "walk_time": "Total Walk Time",
        "run_speed": "Run Speed (min/mile)",
        "walk_speed": "Walk Speed (min/mile)",
    }

    result_df = pd.DataFrame()
    for col, label in time_columns.items():
        result_df[label] = run_df[col].apply(format_timedelta)

    table_html = result_df.to_html(
        classes="data", header=True, index=False, table_id="pacing_table"
    )

    # Calculate marathon milestones
    milestones_data = milestones(desired_time_without_breaks)
    milestones_df = pd.DataFrame([
        {
            'Milestone': name,
            'Notes': data['notes'],
            'Distance (miles)': f"{data['distance']:.1f}",
            'Target Time': data['time']
        }
        for name, data in milestones_data.items()
    ])
    
    milestones_html = milestones_df.to_html(
        classes="data", header=True, index=False, table_id="milestones_table"
    )

    # Assumptions
    assumptions = [
        f"Bathroom breaks: {BATHROOM_BREAK_TIME} min, Water stops: {WATER_STOP_TIME} min",
        f"Walk: {format_timedelta(WALK_INTERVAL)} every interval at {format_timedelta(WALK_SPEED)}/mile",
        f"Run intervals: {RUN_MIN}-{RUN_MAX} min, Distance: {MARATHON_DISTANCE} miles",
        "Strategy: Run-walk intervals for energy conservation"
    ]

    return render_template(
        "calculate.html",
        table_html=table_html,
        milestones_html=milestones_html,
        walk_interval_note=f"Walk Interval: {format_timedelta(WALK_INTERVAL)} at {format_timedelta(WALK_SPEED)}/mile",
        assumptions=assumptions,
        marathon_time_display=format_timedelta(desired_time),
        required_pace=format_timedelta(desired_pace),
    )


if __name__ == "__main__":
    app.run()
