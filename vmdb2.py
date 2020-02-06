import subprocess

def _runcmd(ctx, argv):
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate("")
    ctx['stdout'] = stdout
    ctx['stderr'] = stderr
    ctx['exit'] = p.returncode

def _binary(basename):
    return os.path.join(srcdir, basename)

def given_file(ctx, filename=None):
    with open(filename, 'wb') as f:
        f.write(get_file(filename))
 
def run_vmdb2(ctx, filename=None, output=None):
    vmdb2 = _binary('vmdb2')
    _runcmd(ctx, [vmdb2, filename, '-v', '--output', output])

def exit_code_is(ctx, exit_code=None):
    assert_eq(ctx['exit'], int(exit_code))

def stdout_contains(ctx, pat1=None, pat2=None):
    stdout = ctx.get('stdout', b'').decode('utf-8')
    i = stdout.find(pat1)
    assert i >= 0, "pat1 not found"
    i = stdout[i:].find(pat2)
    assert i >= 0, "pat2 not found after pat1"

def stdout_does_not_contain(ctx, pat1=None):
    stdout = ctx.get('stdout', b'').decode('utf-8')
    i = stdout.find(pat1)
    assert i == -1, "pattern found"
