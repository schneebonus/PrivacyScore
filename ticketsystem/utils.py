
import re

class utils():
    def extract_uid(responce):
        responce_utf8 = responce[0].decode("utf-8")
        # Example: 5 (UID 38)
        regex_uid = "^.*\(UID (.*)\)>*$"
        matchObj = re.match(regex_uid, responce_utf8)
        if matchObj is not None:
            uid = matchObj.group(1)
            return uid
        return 0
