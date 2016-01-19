#!/usr/bin/env python

# Test Inform and the Informant Generator

# Imports {{{1
from __future__ import print_function, unicode_literals
from runtests import (
    cmdLineOpts, writeSummary, succeed, fail, info, status, warning
)
from inform import indent
from textwrap import dedent
from difflib import Differ
from importlib import import_module
import re
import io
import sys
import os


# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()


# Utilities {{{1
def format(text):
    try:
        if '\n' in text:
            return '\n' + indent(text, '        ')
        else:
            return text
    except:
        return text

invokeTimeRegex = r"(?<=Invoked as )'.*' on .*(?=\.)"
def stripInvokeTime(text):
    return re.sub(invokeTimeRegex, '<exe> on <date>', text)

# showDiff {{{2
def showDiff(achieved, expected, indent=''):
    diff = Differ().compare(
        expected.splitlines(),
        achieved.splitlines()
    )
    for each in diff:
        if each[0] == '+':
            print(indent+succeed(each))
        elif each[0] == '-':
            print(indent+info(each))
        elif each[0] == '?':
            print(indent+status(each))
        else:
            print(indent+each)


# Case class {{{1
class Case():
    names = set()
    inform = import_module('inform')

    def __init__(self, name, stimulus, stdout='', stderr='', logfile=''):
        self.name = name
        self.stimulus = stimulus.strip()
        assert name not in Case.names
        Case.names.add(name)
        self.expected_output = stdout.strip()
        self.expected_error = stderr.strip()
        self.expected_log = logfile.strip()

    def __str__(self):
        return '%s<%s>' % (self.__class__.__name__, self.name)

    __repr__ = __str__

    def run(self):
        try:
            with io.StringIO() as stdout, \
                 io.StringIO() as stderr, \
                 io.StringIO() as logfile:
                test_locals = {
                    'stdout': stdout,
                    'stderr': stderr,
                    'logfile': logfile,
                }
                test_globals = Case.inform.__dict__
                exec(self.stimulus, test_globals, test_locals)
                self.output = stdout.getvalue().strip()
                self.error = stderr.getvalue().strip()
                self.log = stripInvokeTime(logfile.getvalue().strip())

        except Exception as err:
            return (self.name, self.stimulus, str(err), None, 'exception')

        if self.error != self.expected_error:
            return (self.name, self.stimulus, self.error, self.expected_error, 'stderr result')
        if self.output != self.expected_output:
            return (self.name, self.stimulus, self.output, self.expected_output, 'stdout result')
        if self.log != self.expected_log:
            return (self.name, self.stimulus, self.log, self.expected_log, 'logfile result')


# Stop class {{{1
class Exit(Case):
    def __init__(self):
        pass

    def run(self):
        sys.exit('TERMINATING TESTS UPON DEVELOPER REQUEST')

# Test cases {{{1
captureAll = ', '.join([
    'logfile=logfile',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name="inform"',
])
noLog = ', '.join([
    'logfile=False',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name="inform"',
])
fmtStim = dedent("""\
    Inform({stdargs})
    def func1():
        def func2():
            def func3():
                lvl = 3
                try:
                    display(fmt('func3 -> {{lvl}}', _lvl={lvl}))
                except KeyError as err:
                    display("'lvl' not found in func3")
            lvl = 2
            try:
                display(fmt('func2 -> {{lvl}}', _lvl={lvl}))
            except KeyError as err:
                display("'lvl' not found in func2")
            func3()
        lvl = 1
        try:
            display(fmt('func1 -> {{lvl}}', _lvl={lvl}))
        except KeyError as err:
            display("'lvl' not found in func1")
        func2()
    lvl = 0
    try:
        display(fmt('func0 -> {{lvl}}', _lvl={lvl}))
    except KeyError as err:
        display("'lvl' not found in func0")
    func1()
""")
testCases = [
    Case(
        name='endeavor',
        stimulus=dedent('''
            Inform({stdargs})
            output('this is a test.')
        '''.format(stdargs=noLog)),
        stdout="this is a test.",
    ),
    Case(
        name='kestrel',
        stimulus=dedent('''
            Inform({stdargs})
            log('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='overspend',
        stimulus=dedent('''
            Inform({stdargs})
            output('This', 'is', 'a', 'test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='alarm',
        stimulus=dedent('''
            Inform({stdargs})
            output('This', 'is', 'a', 'test', sep='_', end='.')
        '''.format(stdargs=captureAll)),
        stdout="This_is_a_test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This_is_a_test.
        '''),
    ),
    Case(
        name='harden',
        stimulus=dedent('''
            Inform({stdargs})
            log('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='outflank',
        stimulus=dedent('''
            Inform(verbose=True, {stdargs})
            comment('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='elope',
        stimulus=dedent('''
            Inform({stdargs})
            comment('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='sunset',
        stimulus=dedent('''
            Inform(narrate=True, {stdargs})
            narrate('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='wheezy',
        stimulus=dedent('''
            Inform({stdargs})
            narrate('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='claim',
        stimulus=dedent('''
            Inform({stdargs})
            display('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='behind',
        stimulus=dedent('''
            Inform(quiet=True, {stdargs})
            display('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is a test.
        '''),
    ),
    Case(
        name='overhead',
        stimulus=dedent('''
            Inform({stdargs})
            debug('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="inform DEBUG: This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform DEBUG: This is a test.
        '''),
    ),
    Case(
        name='instill',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="inform warning: This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform warning: This is a test.
        '''),
    ),
    Case(
        name='blister',
        stimulus=dedent('''
            Inform({stdargs})
            error('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="inform error: This is a test.",
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform error: This is a test.
        '''),
    ),
    Case(
        name='lattice',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a test.')
            codicil('This is an appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform warning: This is a test.
                This is an appendage.
        '''),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform warning: This is a test.
                This is an appendage.
        '''),
    ),
    Case(
        name='seventh',
        stimulus=dedent('''
            Inform({stdargs})
            error()
            codicil('This is the first appendage.')
            codicil('This is the second appendage.')
            codicil('This is the third appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error: 
                This is the first appendage.
                This is the second appendage.
                This is the third appendage.
        '''),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform error: 
                This is the first appendage.
                This is the second appendage.
                This is the third appendage.
        '''),
    ),
    Case(
        name='primary',
        stimulus=dedent(r'''
            Inform({stdargs})
            error()
            codicil('This is the first appendage.')
            codicil('This is the second appendage,\n   and the third.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error: 
                This is the first appendage.
                This is the second appendage,
                   and the third.
        '''),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform error: 
                This is the first appendage.
                This is the second appendage,
                   and the third.
        '''),
    ),
    Case(
        name='sensitize',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is main message.')
            codicil('This is the first appendage.')
            codicil('This is the second appendage.')
            codicil('This is the third appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            This is main message.
            This is the first appendage.
            This is the second appendage.
            This is the third appendage.
        '''),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            This is main message.
            This is the first appendage.
            This is the second appendage.
            This is the third appendage.
        '''),
    ),
    Case(
        name='mullah',
        stimulus=dedent(r'''
            Inform({stdargs})
            error('Error message.\nAdditional info.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error:
                Error message.
                Additional info.
        '''),
        logfile=dedent('''
            Invoked as <exe> on <date>.
            inform error:
                Error message.
                Additional info.
        '''),
    ),
    Case(
        name='goner',
        stimulus=fmtStim.format(lvl=0, stdargs=noLog),
        stdout=dedent('''
            func0 -> 0
            func1 -> 1
            func2 -> 2
            func3 -> 3
        '''),
    ),
    Case(
        name='shadow',
        stimulus=fmtStim.format(lvl=-1, stdargs=noLog),
        stdout=dedent('''
            'lvl' not found in func0
            func1 -> 0
            func2 -> 1
            func3 -> 2
        '''),
    ),
    Case(
        name='curdle',
        stimulus=fmtStim.format(lvl=-2, stdargs=noLog),
        stdout=dedent('''
            'lvl' not found in func0
            'lvl' not found in func1
            func2 -> 0
            func3 -> 1
        '''),
    ),
]


# Run tests {{{1
testsRun = 0
failures = 0
for case in testCases:
    testsRun += 1
    if printTests:
        print(status('Trying %d (%s):' % (testsRun, case.name)), case.stimulus)

    failure = case.run()

    if failure:
        failures += 1
        name, stimulus, result, expected, kind = failure
        print(fail('Unexpected %s (%s):' % (kind, failures)))
        print(info('    Case    :'), name)
        print(info('    Given   :'), format(stimulus))
        print(info('    Result  :'), format(result))
        print(info('    Expected:'), format(expected))
        if result and expected:
            print(info('    Diff:'))
            showDiff(result, expected, indent=8*' ')


# Print test summary {{{1
numTests = len(testCases)
assert testsRun == numTests, "Incorrect number of tests run (%s of %s)." % (testsRun, numTests)
if printSummary:
    print('%s: %s tests run, %s failures detected.' % (
        fail('FAIL') if failures else succeed('PASS'), testsRun, failures
    ))

writeSummary(testsRun, failures)
sys.exit(int(bool(failures)))

# vim: set sw=4 sts=4 et:
