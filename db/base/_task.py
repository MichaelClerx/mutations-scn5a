#!/usr/bin/env python3
#
# Provides connections to the mutation database.
#
import base
import os
import csv
import imp
import sys
import time
import fnmatch
import traceback


class Task(object):
    """
    Defines a task that can be run.

    Each task is identified by a unique, short name.
    """
    def __init__(self, name):
        super(Task, self).__init__()
        self._name = str(name)
        self._name.strip()
        self._newline = True
        self._data_subdir = None
    def csv_reader(self, filehandle):
        """
        Returns a csv reader for the given filehandle, initialized with the
        default options.
        """
        return csv.reader(filehandle, **base.CSV_OPTIONS)
    def csv_writer(self, filehandle):
        """
        Returns a csv writer for the given filehandle, initialized with the
        default options.
        """
        return csv.writer(filehandle, **base.CSV_OPTIONS)
    def data_in(self, name):
        """
        Returns the path of a data input file with the given name.
        """
        return os.path.join(base.DIR_DATA_IN, name)
    def data_out(self, name):
        """
        Returns the path of a data output file with the given name.
        """
        if self._data_subdir:
            return os.path.join(base.DIR_DATA_OUT, self._data_subdir, name)
        else:
            return os.path.join(base.DIR_DATA_OUT, name)
    def figure_in(self, name):
        """
        Returns the path of a figure input file with the given name.
        """
        return os.path.join(base.DIR_FIGURE_IN, name)
    def figure_out(self, name):
        """
        Returns the path of a figure output file with the given name.
        """
        return os.path.join(base.DIR_FIGURE_OUT, name)
    def name(self):
        """
        Returns this task's name.
        """
        return self._name
    def run(self):
        """
        Runs this task.

        Returns ``True`` only if the task completes without errors.
        """
        out = sys.stdout
        err = sys.stderr
        try:
            sys.stdout = sys.stderr = self
            self._run()
            return True
        except Exception:
            self.write(traceback.format_exc())
            return False
        finally:
            sys.stdout = out
            sys.stderr = err
    def _run(self):
        """
        Internal run() method.
        """
        raise NotImplementedError
    def _set_data_subdir(self, subdir):
        """
        Sets a subdirectory in data_out for this task to write to.
        """
        if subdir is None:
            self._data_subdir = None
        else:
            # Get absolute path, check if inside data_out
            d = os.path.abspath(base.DIR_DATA_OUT)
            e = os.path.abspath(os.path.join(base.DIR_DATA_OUT, subdir))
            if e[:len(d)] != d:
                raise Exception('Data subdir cannot lie outside main data dir')
            # Check if new path exists
            if not os.path.isdir(e):
                # Don't create new directories if even data_out doesn't exist
                if not os.path.isdir(d):
                    raise Exception('Path not found: ' + d)
                os.makedirs(e)
            # Store relative path from data_out to subdir
            self._data_subdir = os.path.relpath(e, d)
    def write(self, text):
        """
        Prints some output to the screen
        """
        if text == '\n':
            sys.__stdout__.write('\n')
            self._newline = True
            return
        if self._newline:
            sys.__stdout__.write('[' + time.strftime('%H:%M:%S') + ' '
                + self._name + '] ')
            self._newline = False
        sys.__stdout__.write(text)


class TaskRunner(object):
    """
    Runs one or more tasks.
    """
    def __init__(self, tasks=None):
        self._tasks = []
        if tasks:
            for task in tasks:
                if isinstance(task, Task):
                    self._tasks.add(task)
                else:
                    raise ValueError('All tasks must extend the `Task`'
                        ' interface.')

    def run(self):
        """
        Runs all the tasks in this runner.
        """
        print('Running')
        for task in self._tasks:
            print('Running ' + task.name())
            if not task.run():
                print('-'*40)
                print('Error in task: ' + task.name())
                break
        print('Done')

    def add_dir(self, directory):
        """
        Recursively adds all tasks found in the given directory.
        """
        def scan(directory):
            for filename in os.listdir(directory):
                path = os.path.join(directory, filename)
                if os.path.isdir(path):
                    #print('Descending into: ' + path)
                    scan(path)
                elif filename[-3:] == '.py':
                    #print('Adding: ' + path)
                    self.add_file(path)
        scan(directory)

    def add_file(self, filename):
        """
        Adds all tasks found in the given file.

        The filename must end in '.py'.
        """
        if filename[-3:] != '.py':
            raise ValueError('All given filenames must end in .py')
        path, name = os.path.split(filename)
        path = os.path.abspath(path)
        name = name[:-3]
        (filename, path, description) = imp.find_module(name, [path])
        mod = imp.load_source(name, path)
        if 'tasks' in dir(mod):
            self.add_tasks(mod.tasks())

    def add_task(self, task):
        """
        Adds a task to this runner's task list.
        """
        if not isinstance(task, Task):
            raise ValueError('All tasks must extend the Task interface.')
        self._tasks.append(task)

    def add_tasks(self, tasks):
        """
        Adds multiple tasks to this runner's task list.
        """
        for task in tasks:
            if not isinstance(task, Task):
                raise ValueError('All tasks must extend the Task interface.')
            self._tasks.append(task)
