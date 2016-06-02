#!/usr/bin/env python

# Copyright (c) 2009, Shinichiro Hamaji
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the <ORGANIZATION> nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import difflib
import fileinput
import re
import sys

# ANSI colors
RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN = [1,2,3,4,5,6]

def brightFG(ansi_number):  # bright and/or bold, depends on terminal
    return '\033[1;3%dm' % ansi_number

def darkFG(ansi_number):
    return '\033[0;3%dm' % ansi_number

def brightBG(ansi_number):
    return '\033[1;4%dm' % ansi_number

def darkBG(ansi_number):
    return '\033[0;4%dm' % ansi_number

CANCEL = '\033[0m'

class ColorDiff:
    DEL = dict(text=brightFG(RED), trailingSpace=darkBG(RED))
    DEL_UNCHANGED = dict(text=darkFG(RED), trailingSpace=darkBG(RED))
    INS = dict(text=brightFG(BLUE), trailingSpace=darkBG(BLUE))
    INS_UNCHANGED = dict(text=darkFG(BLUE), trailingSpace=darkBG(BLUE))

    def __init__(self):
        self.clear()

    def clear(self):
        self.minus_buf = ''
        self.plus_buf = ''

    def withColors(self, colors, tokens):
        output = [colors['text']]
        for tok in tokens:
            match = re.match('( *)(\r*\n)', tok)
            if match:
                trailing_space, newline = match.groups()
                output += [colors['trailingSpace'], trailing_space, CANCEL, newline, colors['text']]
            else:
                output += [tok]
        return ''.join(output)

    def tokenize(self, line):
        r = re.findall('[a-zA-Z0-9_]+| *\r*\n| +|.', line, re.DOTALL)
        return r

    def flushAll(self):
        if self.minus_buf and self.plus_buf:
            minus = ''
            plus = ''
            minus_buf = self.tokenize(self.minus_buf)
            plus_buf = self.tokenize(self.plus_buf)
            for op, ms, me, ps, pe in difflib.SequenceMatcher(
                None, minus_buf, plus_buf).get_opcodes():
                m = minus_buf[ms:me]
                p = plus_buf[ps:pe]
                if op == 'delete':
                    minus += self.withColors(self.DEL, m)
                elif op == 'equal':
                    minus += self.withColors(self.DEL_UNCHANGED, m)
                    plus += self.withColors(self.INS_UNCHANGED, p)
                elif op == 'insert':
                    plus += self.withColors(self.INS, p)
                elif op == 'replace':
                    minus += self.withColors(self.DEL, m)
                    plus += self.withColors(self.INS, p)
            sys.stdout.write(minus + plus + CANCEL)
        else:
            self.outputMinus(self.minus_buf)
            self.outputPlus(self.plus_buf)
        self.clear()

    def outputPlus(self, tokens):
        sys.stdout.write(self.withColors(self.INS, tokens) + CANCEL)

    def outputMinus(self, tokens):
        sys.stdout.write(self.withColors(self.DEL, tokens) + CANCEL)

    def run(self):
        for line in fileinput.input():
            if line.startswith('-'):
                if self.plus_buf:
                    self.flushAll()
                self.minus_buf += line
            elif line.startswith('+'):
                if self.minus_buf:
                    self.plus_buf += line
                else:
                    self.outputPlus(self.tokenize(line))
            else:
                self.flushAll()
                sys.stdout.write(line)
        self.flushAll()

ColorDiff().run()
