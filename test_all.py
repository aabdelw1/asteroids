from __future__ import absolute_import

######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

from builtins import str
from builtins import object
import collections
import io
import multiprocessing as mproc
import sys
import traceback

import runner
import text_display
from test_one import case_params, run_method, run_kwargs

try:
    import pilot
    studentExc = None
except Exception as e:
    studentExc = e

TIMEOUT = 10

FAILURE_EXCEPTION='exception_raised'
FAILURE_TIMEOUT='execution_time_exceeded'

GradingTask = collections.namedtuple( 'GradingTask',
                                      ('case_num', 'method_name', 'weight') )

TASKS = ( GradingTask( 1, 'estimate', 4 ),
          GradingTask( 2, 'estimate', 4 ),
          GradingTask( 3, 'estimate', 4 ),
          GradingTask( 4, 'estimate', 4 ),
          GradingTask( 5, 'estimate', 4 ),
          GradingTask( 6, 'estimate', 4 ),
          GradingTask( 7, 'estimate', 4 ),
          GradingTask( 8, 'estimate', 4 ),
          GradingTask( 1, 'navigate', 1 ),
          GradingTask( 2, 'navigate', 1 ),
          GradingTask( 3, 'navigate', 1 ),
          GradingTask( 4, 'navigate', 1 ),
          GradingTask( 5, 'navigate', 1 ),
          GradingTask( 6, 'navigate', 1 ),
          GradingTask( 7, 'navigate', 1 ),
          GradingTask( 8, 'navigate', 1 ))

def truncate_runlog(runlog, begin_lines=10, end_lines=10):
    lines = runlog.splitlines()
    if len(lines) <= begin_lines + end_lines:
        return str(runlog)
    else:
        return '\n'.join( lines[:begin_lines] + lines[-end_lines:] )

class SingleCaseGrader(object):

    def __init__(self):
        # Using a Manager here to create the Queue resolves timeout
        # issue on Windows.
        self.result_queue = mproc.Manager().Queue(1)

    def _reset(self):
        while not self.result_queue.empty():
            self.result_queue.get()

    def run(self, method_name, case_num):

        self._reset()
        
        display = text_display.TextRunnerDisplay( fout = io.StringIO() )
        msg = ''
        
        try:
            kwargs = run_kwargs( case_params(case_num) )
            retcode,t = run_method( method_name )( display = display, **kwargs )
        except Exception as e:
            retcode = FAILURE_EXCEPTION
            t = 1000
            msg = traceback.format_exc()
#            msg = str(e) + ': ' + str(e.message)

        self.result_queue.put( (retcode,t,display.fout.getvalue() + '\n' + msg) )

class MultiCaseGrader(object):

    def __init__(self,
                 fout,
                 tasks = TASKS,
                 timeout=TIMEOUT):
        self.fout = fout
        self.tasks = tuple(tasks)
        self.timeout = timeout

    def run(self):

        score=0
        max_score=0
        
        for task in self.tasks:

            scg = SingleCaseGrader()
            test_process = mproc.Process(target = scg.run, args=(task.method_name,task.case_num))
            runlog = ''

            try:
                test_process.start()
                test_process.join( self.timeout )
            except Exception as exp:
                retcode = FAILURE_EXCEPTION

            if test_process.is_alive():
                test_process.terminate()
                retcode = FAILURE_TIMEOUT
                
            if not scg.result_queue.empty():
                retcode,t,runlog = scg.result_queue.get()

            case_score = task.weight if retcode == runner.SUCCESS else 0
                
            self.fout.write("begin case %d, method %s\n"
                            % (task.case_num, task.method_name))
            self.fout.write(truncate_runlog(runlog))
            self.fout.write("end case %d, method %s, result: %s  (%d/%d)\n"
                            % (task.case_num, task.method_name, retcode, case_score, task.weight))
            self.fout.write('\n\n')

            score += case_score
            max_score += task.weight

        percent = int( round( float(score * 100) / float(max_score) ) )
        self.fout.write("raw score: %d/%d\n" % (score, max_score))
        self.fout.write("score: %d\n" % percent)
#        self.fout.write("overall score:  %d/%d\n" % (score, max_score))
            
if __name__ == '__main__':
    mcg = MultiCaseGrader(sys.stdout)
    mcg.run()
