import os
import sys
import json
from datetime import datetime
import subprocess


class LogEntry():
    __buildid_query = '''.[]["plays"][]["tasks"][]["hosts"][]
                         ["invocation"]["module_args"]["zuul"]["build"] 
                         | values'''

    __steptime_query = '''[.[]["plays"][]["tasks"][]
                              | select(.["task"]["name"]
                                | contains("Install package dependencies for the build")
                                  or contains("Run a full Contrail VNC build")
                                  or contains("Run unittest script"))
                              | [
                                 (.["task"]["name"]),
                                 (.["hosts"][]["delta"] )
                               ]]
                           '''

    def __init__(self, filepath):
        self.source = filepath

        zcat_out = subprocess.check_output(["zcat", filepath], shell=False)

        jq_buildid = subprocess.Popen(["jq", "-r", self.__buildid_query],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        self.build_id = jq_buildid.communicate(zcat_out)[0].strip() or 'unknown_label'

        jq_steps_times = subprocess.Popen(["jq", "-c", self.__steptime_query],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE)
        raw_steps_times = json.loads(jq_steps_times.communicate(zcat_out)[0])

        self.steps_times = ((step,
                            datetime.strptime(time, "%H:%M:%S.%f").time())
                            for step, time
                            in raw_steps_times
                            if time)
        self.date = datetime.fromtimestamp(os.path.getmtime(filepath))


if __name__ == '__main__':
    name = sys.argv[1]
    print list(LogEntry(name).steps_times)
