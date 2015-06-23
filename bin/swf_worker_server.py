#!/usr/bin/env python

import argparse
import os
import re
from subprocess import call


if __name__ == '__main__':
    from luigi_swf.log import configure_logging
    files_preserve = configure_logging()
    import luigi.configuration
    from luigi_swf.worker import WorkerServer
    parser = argparse.ArgumentParser(description='start/stop SWF worker(s)')
    parser.add_argument('action', choices=['start', 'stop'])
    parser.add_argument('--identity', default=None)
    parser.add_argument('--task-list', default=None)
    args = parser.parse_args()
    config = luigi.configuration.get_config()
    if args.action == 'start':
        if args.identity is None or args.identity == '':
            # Start all
            num_workers = config.getint('swfscheduler', 'num-workers')
            for worker_idx in xrange(num_workers):
                worker_args = [__file__, 'start', '--identity',
                               str(worker_idx)]
                if args.task_list is not None:
                    worker_args += ['--task-list', args.task_list]
                call(worker_args)
        else:
            # Start one
            server = WorkerServer(
                identity=args.identity, version='unspecified',
                task_list=args.task_list)
            server.start()
    elif args.action == 'stop':
        if args.identity is None or args.identity == '':
            # Stop all
            pid_dir = config.get('swfscheduler', 'worker-pid-file-dir')
            re_pid = re.compile(r'^swfworker\-(.+)\.pid(\-waiting)?$')
            for pid_file in os.listdir(pid_dir):
                pid_match = re_pid.match(pid_file)
                if pid_match is None:
                    continue
                identity = pid_match.groups()[0]
                server = WorkerServer(identity=identity,
                                      version='unspecified')
                server.stop()
        else:
            # Stop one
            server = WorkerServer(identity=args.identity,
                                  version='unspecified')
            server.stop()
