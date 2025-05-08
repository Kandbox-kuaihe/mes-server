def get_field_val_various(self, field_name, cd_char, length=None):
        for record in self.sp_various:
            if cd_char is None or record.cd_char == cd_char:
                value = getattr(record, field_name, "")
                return value.ljust(length)[:length] if length else value
        return ""