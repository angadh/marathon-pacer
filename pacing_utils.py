import datetime

MARATHON_MILESTONES = {
    '5k': {'distance': 3.1, 'notes': 'First checkpoint - settle into pace'},
    '10k': {'distance': 6.2, 'notes': 'Quarter mark - energy still high'},
    '15k': {'distance': 9.3, 'notes': '15k mark - maintain rhythm'},
    '13.1K': {'distance': 13.1, 'notes': 'Halfway point - halfway there!'},
    '25k': {'distance': 15.5, 'notes': '25k mark - getting serious'},
    '20 Mile': {'distance': 20.0, 'notes': 'The Wall - push through'},
    '22 Mile': {'distance': 22.0, 'notes': '22 mile - almost there'},
    '23 Mile': {'distance': 23.0, 'notes': '23 mile - final push'},
    '24 Mile': {'distance': 24.0, 'notes': '24 mile - home stretch'},
    '25 Mile': {'distance': 25.0, 'notes': '25 mile - final mile'},
    'Finish': {'distance': 26.2, 'notes': 'Marathon complete!'}
}

def race_times(hours=0, minutes=0, seconds=0):
    """
    Convert run time from minutes to hours, minutes and seconds.
    """
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)


def format_timedelta(td):
    """
    Format a timedelta object as a string.
    """
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)

    result_str = f"{seconds:02d}s"

    if hours > 0:
        result_str = f"{hours:d}h:{minutes:02d}m:{seconds:02d}s"
    else:
        if minutes > 0:
            result_str = f"{minutes:d}m:{seconds:02d}s"
    return result_str


def milestones(marathon_time, marathon_distance=26.2):
    milestones_dict = MARATHON_MILESTONES.copy()
    for milestone_name, milestone_data in milestones_dict.items():
        milestone_note = milestone_data['notes']
        milestone_time = format_timedelta(marathon_time * ( milestone_data['distance'] / marathon_distance))
        milestones_dict[milestone_name]['time'] = milestone_time
    return milestones_dict