#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime,timezone,timedelta

class TimeUtil():


    def convert_timezone(date_time, offset_hours=0):
        """
        UTC时区转换
        :param date_time: datetime
        :param offset: int (hours)
        :return: datetime
        """
        dt = date_time.replace(tzinfo=timezone.utc)
        tzutc = timezone(timedelta(hours=offset_hours))
        return dt.astimezone(tzutc)
