import pytz

def convert_gmt_to_ist(gmt_time):
    gmt_timezone = pytz.timezone('GMT')
    ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time

    gmt_time = gmt_timezone.localize(gmt_time)
    ist_time = gmt_time.astimezone(ist_timezone)

    # Format IST time to show only time
    ist_time_str = ist_time.strftime('%Y-%m-%d %H:%M')

    return ist_time_str
