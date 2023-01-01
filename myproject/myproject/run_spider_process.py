from subprocess import Popen, PIPE, CalledProcessError


def execute(cmd):
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for stdout_line in p.stdout:
            # print(stdout_line, end='')  # process line here
            yield stdout_line

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
