# tox_core.py
import os
import sys
import tty
import termios
from typing import Callable, List, Dict, Tuple
from collections import OrderedDict

import logging
logging.basicConfig(filename=f"{os.environ.get('HOME','/tmp')}/.tox_core.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


tox_core_root = os.path.dirname(os.path.realpath(__file__))
logging.info(f"tox startup, args={sys.argv}, cwd={os.getcwd()}, __file__={__file__}")

sys.path.insert(0, tox_core_root)

''' Debugging tips:
    1.  Set tox_debugpy=1 to enable debugpy listening on 5690
    2.  Set break_on_main=1 to enable stop in __main__ block instead of here '''
if int(os.environ.get('tox_debugpy',0)) > 0:
    import debugpy
    dbgport=int(os.environ.get('tox_debug_port','5690'))
    debugpy.listen(('0.0.0.0',dbgport))
    sys.stderr.write(f"Waiting for python debugpy client on port {dbgport}\n")
    debugpy.wait_for_client()
    if int(os.environ.get('break_on_main',0)) < 1:
        breakpoint()

from io import StringIO
import re
import bisect
import argparse
import fnmatch
import shutil
from subprocess import call
from os.path import dirname, isdir, realpath, exists, isfile
from os import getcwd, environ, stat
from pwd import getpwuid
from setutils import IndexedSet


toxRootKey:str = "ToxSysRoot"
file_sys_root:str = os.getenv(toxRootKey, "/")
# Swap this for chroot-like testing

stub_counter:int =0
def stub(*msg) -> None:
    global stub_counter
    stub_counter+=1
    sys.stderr.write(f"\033[;33mstub[{stub_counter}] <{msg}>\033[;0m\n")

def set_file_sys_root(d: str) -> str:
    global file_sys_root
    prev = file_sys_root
    file_sys_root = d
    return prev

class UserTrap(BaseException):
    ...
class UserUpTrap(UserTrap):
    ...
class UserDownTrap(UserTrap):
    ...
class UserSelectionTrap(UserTrap):
    ...

class AddEntryAlreadyPresent(BaseException):
    ...

indexFileBase:str = ".tox-index"

home_path:str=os.environ.get('HOME',None)

def abbreviate_path(dest_path:str,ix_path:str):
    ''' Render shortest-meaningful representation of dest_path '''
    def home_relative(dest_path:str):
        return '~' + dest_path[len(home_path):]
    if dest_path.startswith(home_path):
        return home_relative(dest_path)
    if dest_path.startswith(ix_path):
        return dest_path[len(ix_path)+1:]
    if not dest_path[0] == '/':
        if pwd()==home_path:
            return '~/'+dest_path
        return './'+dest_path
    return dest_path



def pwd() -> str:
    """Return the $PWD value, which is nicer inside
    trees of symlinks, but fallback to getcwd if it's not
    set"""
    return environ.get("PWD", getcwd())

def getraw_kbd() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            ch = sys.stdin.read(1)
            yield ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def dirContains(parent: str, unk: str) -> bool:
    """ Does parent dir contain unk dir? """
    return realpath(unk).startswith(realpath(parent))


def trace(msg: str) -> None:
    sys.stderr.write(f"\033[;33m{msg}\033[;0m\n")


class IndexContent(list):
    ''' Each index entry is a [path,priority] tuple.  Higher priority numbers cause
    an entry to move to the top of the match list.  Default priority is 1.  Absent
    priority, entries or ordered by ascending length alone. '''
    def __init__(self, path: str):
        self.path: str = path
        self.protect: bool = False
        self.outer = None  # If we are chaining indices

        with open(self.path, "r") as f:
            for line in f.readlines():
                path,_,priority=line.rstrip().partition(' ')
                if not path or path[0]=='#':
                    continue
                try:
                    pri=int(priority)
                except:
                    pri=1
                self.append((path,pri))

    def Empty(self) -> bool:
        """ Return true if index chain has no entries at all """
        if len(self):
            return False
        if self.outer is None:
            return True
        return self.outer.Empty()

    def indexRoot(self) -> str:
        """ Return dir of our index file """
        return dirname(self.path)

    def absPath(self, relDir: str) -> str:
        """ Return an absolute path if 'relDir' isn't already one """
        if relDir[0] == "/":
            return relDir
        return "/".join([self.indexRoot(), relDir])

    def relativePath(self, dir: str) -> str:
        """ Convert dir to be relative to our index root """
        try:
            r = self.indexRoot()
            # If the dir starts with our index root, remove that:
            if dir.index(r) == 0:
                return dir[len(r) + 1 :]
        except:
            pass
        return dir

    def addDir(self, xdir: str, priority: int) -> bool:
        dir = self.relativePath(xdir)
        if dir in self:
            return False  # no change
        entry=(dir,priority)
        n = bisect.bisect([p[0] for p in self], dir)
        try:
            if self[n-1][0]==dir:
                if self[n-1][1] == priority:
                    raise AddEntryAlreadyPresent()
                self[n-1]=entry  # Update existing entry
                return True
        except IndexError:
            ...
        self.insert(n, entry)
        return True

    def delDir(self, xdir: str) -> bool:
        dir = self.relativePath(xdir)
        for e in self:
            if e[0]==dir:
                self.remove(e)
                return True
        return False

    def clean(self) -> None:
        # Remove dead paths from index
        okEntries = set()
        for entry in self:
            path=entry[0]
            full = self.absPath(path)
            if not isdir(full):
                sys.stderr.write("Stale dir removed: %s\n" % full)
            else:
                okEntries.add(entry)

        del self[:]
        self.extend(okEntries)
        self.write()
        sys.stderr.write("Cleaned index %s, %s dirs remain\n" % (self.path, len(self)))

    def write(self) ->None:
        # Write the index back to file
        with open(self.path + ".tmp", "w") as f:
            for entry in sorted(self):
                f.write("%s %d\n" % entry)
        os.rename(self.path + ".tmp", self.path)

    def matchPaths(self, patterns:List[str], fullDirname:bool=False) ->List[str]:
        """ Returns matches of items in the index. """

        # Identify all the potential matches, filter by all patterns:
        cand_entries = self[:]
        for pattern in patterns:
            qual_entries = []
            for entry in cand_entries:
                path=entry[0]
                for frag in path.split("/"):
                    if fnmatch.fnmatch(frag, pattern):
                        # If fullDirname is set, we'll render an absolute path.
                        # Or... if the relative path is not a dir, we'll also
                        # render it as absolute.  This allows for cases where an
                        # outer index path happens to match a local relative path
                        # which isn't indexed.
                        if fullDirname or not isdir(path):
                            qual_entries.append((self.absPath(path),entry[1]))
                        else:
                            qual_entries.append((path,entry[1]))
            cand_entries = qual_entries

        # Remove dupes:
        xs = IndexedSet()
        for entry in cand_entries:
            xs.add(entry)
        if self.outer is not None:
            # We're a chain, so recurse:
            pp = self.outer.matchPaths(patterns, True)
            xs = xs.union(pp)
        return sorted(list(xs),key=lambda entry: len(entry[0])/entry[1])


class AutoContent(list):
    """ Reader/parser of the .tox-auto files """

    def __init__(self, path):
        self.path = path
        self.tagsLoc = None
        self.descLoc = None
        if path:
            with open(path, "r") as f:
                self.extend(f.readlines())

        lineNdx = 0
        for line in self:

            # Locate the .TAGS and .DESC content:
            if not self.tagsLoc and line.startswith("# .TAGS:"):
                self.tagsLoc = (lineNdx, 8)
            elif not self.descLoc and line.startswith("# .DESC:"):
                self.descLoc = (lineNdx, 8)

            lineNdx += 1

    def tags(self):
        """ Return the value of .TAGS as array of strings """
        if not self.tagsLoc:
            return []
        raw = self[self.tagsLoc[0]][self.tagsLoc[1] :]
        return raw.split()

    def desc(self):
        """ Return the value of .DESC as a string """
        if self.descLoc is None:
            return ""
        return self[self.descLoc[0]][self.descLoc[1] :].rstrip()


def isFileInDir(dir:str, name:str) -> bool:
    """ True if file 'name' is in 'dir' """
    return exists("/".join([dir, name]))


def isChildDir(parent:str, cand:str) -> bool:
    """ Returns true if parent is an ancestor of cand. """
    if cand.startswith(parent) and len(cand) > len(parent):
        return True
    return False


def ownerCheck(xdir:str, filename:str, only_mine:bool) -> bool:
    """Apply ownership rule to file xdir/filename, such that:
    - If only_mine is True, owner of the file must match os.environ['USER']
    - If only_mine is False, we don't care who owns it.
    return True if rule check passes."""
    if not only_mine:
        return True
    owner = stat("/".join((xdir, filename))).st_uid
    user = os.environ.get('USER','root')
    try:
        return getpwuid(owner).pw_name == user
    except KeyError:
        # we can't ident the owner:
        return True


def findIndex(xdir:str=None, only_mine:bool=True) -> IndexContent:
    """Find the index containing current dir or 'xdir' if supplied.  Return HOME/.tox-index as a last resort, or None if there's no indices whatsoever.

    only_mine: ignore indices which don't have $USER as owner on the file.
    """
    if not xdir:
        xdir = pwd()
    global indexFileBase
    if not isChildDir(file_sys_root, xdir):
        xdir = os.path.realpath(xdir)
        if not isChildDir(file_sys_root, xdir):
            if len(xdir) < len(file_sys_root):
                return None
            if xdir != file_sys_root:
                # If we've searched all the way up to the root /, try the
                # user's HOME dir:
                return findIndex(environ["HOME"])
    if isFileInDir(xdir, indexFileBase) and ownerCheck(xdir, indexFileBase, only_mine):
        return "/".join([xdir, indexFileBase])
    if isFileInDir(xdir, indexFileBase) and xdir == environ["HOME"]:
        return "/".join([xdir, indexFileBase])
    # Recurse to parent dir:
    if xdir == file_sys_root:
        # If we've searched all the way up to the root /, try the user's HOME
        # dir:
        return findIndex(environ["HOME"])

    logging.info(f"findIndex returns: xdir={xdir}, HOME={environ['HOME']}, file_sys_root={file_sys_root}")
    return findIndex(dirname(xdir))


def loadIndex(xdir:str=None, deep:bool=False, inner=None) -> IndexContent:
    """Load the index for current xdir.  If deep is specified,
    also search up the tree for additional indices"""
    if xdir and not isdir(xdir):
        raise RuntimeError("non-dir %s passed to loadIndex()" % xdir)

    ix:IndexContent = findIndex(xdir)
    if not ix:
        return None

    ic = IndexContent(ix)
    if not inner is None:
        inner.outer = ic
    if deep and not xdir == environ["HOME"]:
        ix = findIndex(dirname(ic.indexRoot()))  # Bug?
        # ix = findIndex(ic.indexRoot())
        if ix:
            loadIndex(dirname(ix), True, ic)
    return inner if not inner is None else ic


class ResolveMode(object):
    userio = 1  # interact with user, menu-driven
    printonly = 2  # print the match list
    calc = 3  # calculate the match list and return it


def resolvePatternToDir(patterns:List[str], mode:ResolveMode=ResolveMode.userio) -> Tuple[List,str]:
    """ Match patterns to index, choose Nth result or prompt user, return dirname to caller. If printonly, don't prompt, just return the list of matches."""
    # Multiple patterns are handled with recursion: the first is used to select first level, then an index is loaded there and the second pattern is selected

    pattern_0=f'*{patterns[0]}*'
    K=None
    N=None
    next_pattern=1
    try:
        # Scan for K (indicating / or // to select higher-level indexes) and N (number offset in matching set)
        # If K == '//', means 'global': search inner and outer indices
        #    K == '/', means 'skip local': search outer indices only
        for opt in patterns[1:3]:
            if opt in ['/','//']:
                K=opt
                next_pattern+=1
                continue
            try:
                N=int(opt)
                next_pattern+=1
            except:
                ...
    except:
        ...

    # ix is the directory index:
    ix:IndexContent = loadIndex(pwd(), K in ["//", "/"])
    if K == "/":
        # Skip inner index, which can be achieved by walking the index chain up
        # one level
        if ix.outer is not None:
            ix = ix.outer

    if K in ["//", "/"]:
        K = None

    if ix.Empty():
        return (None, "!No matches for [%s]" % "+".join(patterns))

    # Do we have any glob chars in pattern?
    # hasGlob = len([v for v in p if v in ["*", "?"]])
    # if not hasGlob:
    #     # no, make it a wildcard: our default behavior is 'match any part
    #     # of path'
    #     k_pattern="*" + p + "*"
    # else:
    #     k_patterns.append(p)

    def recurse_or_return(matches:List[str],solution:str):
        if not patterns[next_pattern:]:
            if mode == ResolveMode.printonly:
                return printMatchingEntries([rk], rk)
            return (matches,solution)
        solution=realpath(solution)
        os.chdir(solution)
        os.environ['PWD']=solution
        # If there's more patterns, we shall recurse:
        return resolvePatternToDir(patterns[next_pattern:],  mode)

    mx = ix.matchPaths([pattern_0])
    if len(mx) == 0:
        return (None, "!No matches for pattern [%s]" % "+".join(patterns))
    if type(N) is int:
        if abs(N) >= len(mx):
            sys.stderr.write(
                "Warning: Offset %d exceeds number of matches for pattern [%s]. Selecting index %d instead.\n"
                % (N, "+".join(patterns), len(mx)-1)
            )
            N = (len(mx)-1) * (1 if N >= 0 else -1)
        rk = ix.absPath(mx[N][0])
        return recurse_or_return([rk],rk)

    if mode == ResolveMode.printonly:
        return printMatchingEntries(mx, ix)
    if len(mx) == 1:
        rk = ix.absPath(mx[0][0])
        return ([rk], rk)
    if mode == ResolveMode.calc:
        return [mx, None]
    try:
        r0 = promptMatchingEntry(mx, ix)
    except UserUpTrap:
        raise UserUpTrap(dirname(ix.path))

    return recurse_or_return( r0[0],r0[1] )


def printMatchingEntries(mx, ix):
    px = []
    for i in range(1, len(mx) + 1):
        px.append(mx[i - 1][0])
    return (mx, "!" + "\n".join(px))

# Colortable: https://www.lihaoyi.com/post/Ansi/Rainbow256.png
def red(txt:str) -> str:
    return f"\033[1;31m{txt}\033[;0m"
def green(txt:str) -> str:
    return f"\033[38;5;37m{txt}\033[;0m"
def yellow(txt:str) -> str:
    return f"\033[;33m{txt}\033[;0m"
def grey(txt:str) -> str:
    return f"\033[38;5;8m{txt}\033[;0m"
def purp(txt:str) -> str:
    return f"\033[38;5;13m{txt}\033[;0m"


def displayMatchingEntries(dx:OrderedDict,ix_path:str) -> None:
    menu_items=[]
    for i in dx:
        if i[0] == '%':
            menu_items.append(f"{red(i[1:])}{grey(dx[i][0])}")
        else:
            sys.stderr.write(f"  {dx[i][0]} {red(i)}\n")
    sys.stderr.write('   '.join(menu_items))
    sys.stderr.write('\n')

def prompt(msg:str,defValue:str,handler:Callable[[str],str]) -> str:
    # Ansi codes from https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
    #  esc[nnD << Move cursor left nn columns
    #  esc[K << Clear to end of line
    #  esc[s << Save cursor position
    #  esc[u << Restore saved cursor position
    try:
        value=defValue
        while True:
            sys.stderr.write(f"\033[99D \033[K \033[;33m{msg}:\033[;0m {value}")
            sys.stderr.flush()
            c = next(getraw_kbd())
            value = handler(c)
    finally:
        sys.stderr.write('\n')


def multiple_numeric_candidates(buff:str, dx:OrderedDict):
    # prompt_editor calls this to find out if a numeric entry matches
    # more than one dx candidate -- which means we have to wait for more
    # digits
    seq=( k for k in dx if k.startswith(buff))
    next(seq)
    try:
        next(seq)
    except StopIteration:
        return False
    return True

def prompt_editor(vstrbuff:List[str],dx:OrderedDict,c:str) -> str:
    # this is called from prompt() for each char read from kbd.  If we
    # return a buffer, that becomes the new edit contents.  If we
    # throw a trap, that bubbles up to the editor's caller.
    logging.info(f"prompt_editor({ord(c)}:{c})")
    if ord(c) == 3: # Ctrl+C
        raise KeyboardInterrupt
    elif ord(c) == 127:  # Backspace
        vstrbuff[0] = vstrbuff[0][:-1]
        logging.info(f"Erase, now: {vstrbuff[0]}")
        return vstrbuff[0]
    elif ord(c) == 13: # Enter
        if len(vstrbuff[0]) == 0:
            return vstrbuff[0]
        raise UserSelectionTrap(int(vstrbuff[0]))
    elif ord(c) == 27:  # Esc
        logging.info('[esc]: reset buffer')
        vstrbuff[0]=""
        return vstrbuff[0]
    elif vstrbuff[0]=="0":
        if c=='0':
            raise UserSelectionTrap(0)
        else:
            logging.info('reset buffer')
            vstrbuff[0]=""
    vstrbuff[0]=vstrbuff[0]+c
    try:
        try:
            ofs=int(vstrbuff[0])
            if multiple_numeric_candidates(vstrbuff[0],dx):
                return vstrbuff[0]
            dx[vstrbuff[0]]
            raise UserSelectionTrap(ofs)
        except KeyError:
            vstrbuff[0]=""
            return vstrbuff[0]
        except ValueError:
            ofs=None
        v = dx.get(vstrbuff[0],None) or dx[f"%{vstrbuff[0]}"]
        logging.info(f"User input \"{vstrbuff[0]}\" selects entry [{v}]")
        if v[1]:  # Is there something special we should throw?
            raise v[1]
        raise UserSelectionTrap(v[0],ofs)
    except KeyError:
        logging.info(f"User input [{vstrbuff[0]}] doesn't match anything")
        return vstrbuff[0]

def promptMatchingEntry(mx:List[Tuple[str,int]], ix:IndexContent ) ->Tuple[IndexContent,str]:
    # Prompt user to select from set of matching entries.  Return
    # tuple of (mx, selected-entry)
    def get_selector():
        c = -1
        while True:
            c += 1
            yield c

    sel = iter(get_selector())
    ixdir=dirname(ix.path)
    mx_ord=[ ( abbreviate_path( e[0],ixdir ), e[1], e[0] ) for e in mx ]
    mx_ord=sorted( mx_ord, key=lambda e: len(e[0])/e[1] )
    sys.stderr.write(f"{yellow(':: Index:')} {green(dirname(ix.path))}\n")
    dx = OrderedDict( {str(next(sel)):(m[0],None) for m in mx_ord} )
    dx['%q'] = ('<Quit>',KeyboardInterrupt)
    dx['%\\'] = ('<Up Tree>',UserUpTrap)
    dx['%/'] = ('<Down Tree>', UserDownTrap)
    displayMatchingEntries(dx,dirname(ix.path))
    vstrbuff=["0"]
    try:
        prompt("Choose", 0,lambda c: prompt_editor(vstrbuff,dx,c))
    except UserSelectionTrap as s:
        selection_ofs=s.args[0]
        logging.info(f"UserSelectionTrap:{s}")
        return (mx_ord, mx_ord[selection_ofs][2])
    except KeyboardInterrupt:
        logging.info("User Ctrl+C in promptMatchingEntry")
        return (mx_ord, "!echo Ctrl+C")



def addDirsToIndex(xargs:List[str], recurse:bool):
    # xargs is like '1 dir 1 dir2' , etc.
    priority=1
    try:
        if int(xargs[0]) and len(xargs)==1:
            xargs.append(pwd())
    except:
        if not xargs:
            xargs=[pwd(),priority]

    iargs=iter(xargs)
    for arg in iargs:
        try:
            priority=int(arg)
            continue
        except StopIteration:
            xdir=pwd()
        except:
            xdir=arg
        ix = loadIndex()  # Always load active index for this, even if
                          # the dir we're adding is out of tree

        def xAdd(path:str,priority:int):
            try:
                if ix.addDir(path,priority):
                    ix.write()
                    sys.stderr.write("%s added/updated to %s:%d\n" % (path, ix.path,priority))
                    return
            except AddEntryAlreadyPresent:
                sys.stderr.write("%s is already in the index\n" % path)

        xAdd(xdir,priority)
        if recurse:
            for r, dirs, _ in os.walk(xdir):
                dirs[:] = [d for d in dirs if not d[0] == "."]  # ignore hidden dirs
                for d in dirs:
                    xAdd(r + "/" + d,priority)


def delCwdFromIndex():
    """ Delete current dir from active index """
    cwd = pwd()
    ix = loadIndex()
    if ix.delDir(cwd):
        ix.write()
        sys.stderr.write("%s removed from %s\n" % (cwd, ix.path))
    else:
        sys.stderr.write("%s was not found in the index\n" % cwd)


def editIndex():
    ipath = findIndex()
    print("!!$EDITOR %s" % ipath)


def printIndexInfo(ixpath):
    ix = loadIndex(dirname(ixpath) if ixpath else ixpath, True)
    print("!PWD: %s" % (pwd() if not ixpath else dirname(ixpath)))
    print("Index: %s" % ix.path)
    print("# of dirs in index: %d" % len(ix))
    if environ["PWD"] == ix.indexRoot():
        print("PWD == index root")

    if not ix.outer is None:
        print("   ===  Outer: === ")
        printIndexInfo(ix.outer.path)


def ensureHomeIndex():
    global indexFileBase
    loc = "/".join((environ["HOME"], indexFileBase))
    if not os.path.isfile(loc):
        with open(loc, "w") as ff:
            sys.stderr.write("Tox first-time initialization: creating %s\n" % loc)
            ff.write("# This is your HOME dir .tox-index, try 'to --help' \n")


def createIndexHere():
    if isfile("./" + indexFileBase):
        sys.stderr.write("An index already exists in %s" % environ.get("PWD", getcwd()))
        return False
    with open(indexFileBase, "w") as f:
        f.write("#protect\n")
        sys.stderr.write("Index has been created in %s" % pwd())


def cleanIndex():
    ix = loadIndex()
    ix.clean()


def hasToxAuto(dir:str) -> bool:
    xf = "/".join([dir, ".tox-auto"])
    return isfile(xf), xf


def editToxAutoHere(templateFile:str) -> None:
    has, _ = hasToxAuto(".")
    if not has:
        # Create from template file first time:
        shutil.copyfile(templateFile, "./.tox-auto")
    # Invoke the editor:
    print("!!$EDITOR %s" % ".tox-auto")


def printGrep(pattern, ostream=None):
    if pattern:
        ostream = StringIO()
    else:
        ostream = sys.stdout
    ix = loadIndex()
    sys.stdout.write("!")
    for entry in ix:
        dir=entry[0]
        dir = ix.absPath(dir)
        ostream.write(dir)
        has, autoPath = hasToxAuto(dir)
        if has:
            cnt = AutoContent(autoPath)
            ostream.write(" [.TAGS: %s] " % (",".join(cnt.tags())))
            ostream.write(cnt.desc())
        ostream.write("\n")

    matchCnt = 0
    if not pattern:
        return len(ix) > 0
    else:
        # Match the pattern and print matches
        lines = ostream.getvalue().split("\n")
        for line in lines:
            try:
                vv = re.search(pattern, line)
                if vv:
                    matchCnt += 1
                    print(line)
            except:
                pass

        return matchCnt > 0


if __name__ == "__main__":
    if int(os.environ.get('break_on_main',0)) > 0:
        breakpoint()
    sys.setrecursionlimit(98)
    p = argparse.ArgumentParser(
        """to-foo - quick directory-changer v0.9.1 """
    )
    p.add_argument(
        "-x",
        "--ix-here",
        action="store_true",
        dest="create_ix_here",
        help="Create index in current dir",
    )
    p.add_argument(
        "-r",
        "--recurse",
        action="store_true",
        dest="recurse",
        help="Recursive mode (e.g. for -a add all dirs in subtree)",
        default=False,
    )
    p.add_argument(
        "-a",
        "--add-dir",
        action="store_true",
        dest="add_to_index",
        help="Add to index: <priority> <path> (-r to recurse all)",
    )
    p.add_argument(
        "-d",
        "--del-dir",
        action="store_true",
        dest="del_from_index",
        help="Delete current dir from index",
    )
    p.add_argument(
        "-c", "--cleanup", action="store_true", dest="cleanindex", help="Cleanup index"
    )
    p.add_argument(
        "-q",
        "--query",
        action="store_true",
        dest="indexinfo",
        help="Print index information/location",
    )
    p.add_argument(
        "-e", "--edit", action="store_true", dest="editindex", help="Edit the index"
    )
    p.add_argument(
        "-p",
        "--printonly",
        action="store_true",
        dest="printonly",
        help="Print matches in plain mode",
    )
    # p.add_argument(
    #     "--auto",
    #     "--autoedit",
    #     action="store_true",
    #     dest="autoedit",
    #     help="Edit the local .tox-auto, create first if missing",
    # )
    p.add_argument(
        "-g",
        "--grep",
        action="store_true",
        dest="do_grep",
        help="Match dirnames and .tox-auto search properties against a regular expression",
    )
    # p.add_argument("patterns", nargs='?', help="Pattern(s) to match. If final arg is integer, it is treated as list index. ")
    # p.add_argument(
    # "N", nargs='?', help="Select N'th matching directory, or use '/' or '//' to expand search scope.")
    origStdout = sys.stdout

    try:
        sys.stdout = sys.stderr
        args, vargs = p.parse_known_args()
    finally:
        sys.stdout = origStdout


    patterns = vargs
    empty = True  # Have we done anything meaningful?

    ensureHomeIndex()

    if args.do_grep:
        vv = printGrep(patterns[0] if len(patterns) else None)
        sys.exit(0 if vv else 1)

    # if args.autoedit:
    #     editToxAutoHere("/".join([tox_core_root, "tox-auto-default-template"]))
    #     sys.exit(0)

    if args.create_ix_here:
        createIndexHere()
        empty = False

    if args.add_to_index:
        addDirsToIndex(patterns, args.recurse)
        sys.exit(0)

    elif args.del_from_index:
        delCwdFromIndex()
        empty = False

    if args.indexinfo:
        printIndexInfo(findIndex())
        empty = False

    if args.editindex:
        editIndex()
        sys.exit(0)

    if args.cleanindex:
        cleanIndex()
        empty = False

    if not patterns:
        if not empty:
            sys.exit(0)

        sys.stderr.write("No search patterns specified, try --help\n")
        sys.exit(1)

    rmode = ResolveMode.printonly if args.printonly else ResolveMode.userio
    res = (None,None)
    dirstack=[pwd()]
    while True:
        try:
            res = resolvePatternToDir(patterns, rmode)
            break
        except UserUpTrap as t:
            xdir=dirname(t.args[0])
            if dirstack[-1] == xdir:
                break
            sys.stderr.write(f" ::: Relocating to {xdir}\n")
            dirstack.append(xdir)
            os.chdir(xdir)
            os.environ['PWD'] = xdir
        except UserDownTrap as v:
            if len(dirstack) < 2:
                break
            dirstack=dirstack[:-1]
            xdir=dirstack[-1]
            sys.stderr.write(f" ::: Relocating to {xdir}\n")
            os.chdir(xdir)
            os.environ['PWD'] = xdir


    if res[1]:
        print(res[1])

    sys.exit(0)
