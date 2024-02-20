import pytz

def add_ordinal(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"

def convert_gmt_to_ist(gmt_time):
    gmt_timezone = pytz.timezone('GMT')
    ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time

    gmt_time = gmt_timezone.localize(gmt_time)
    ist_time = gmt_time.astimezone(ist_timezone)

    # Format IST time to show only time
    ist_time_str = ist_time.strftime(f"{add_ordinal(ist_time.day)}-{ist_time.strftime('%b')[:3]}-%y %H:%M").lower()

    return ist_time_str
