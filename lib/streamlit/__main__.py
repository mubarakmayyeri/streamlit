# Copyright 2018 Streamlit Inc. All rights reserved.

"""This is a script which is run when the Streamlit package is executed."""

# Python 2/3 compatibility
from __future__ import print_function, division, absolute_import
# Not importing unicode_literals from __future__ because click doesn't like it.
from streamlit.compatibility import setup_2_3_shims
setup_2_3_shims(globals())

import click


LOG_LEVELS = ['error', 'warning', 'info', 'debug']


@click.group()
@click.option('--log_level', show_default=True, type=click.Choice(LOG_LEVELS))
@click.version_option(prog_name='Streamlit')
@click.pass_context
def main(ctx, log_level='info'):
    """Main app entrypoint."""

    if log_level:
        import streamlit.logger
        streamlit.logger.set_log_level(log_level.upper())


@main.command('help')
@click.pass_context
def help(ctx):
    """Print this help message."""
    # Pretend user typed 'streamlit --help' instead of 'streamlit help'.
    import sys
    assert len(sys.argv) == 2  # This is always true, but let's assert anyway.
    sys.argv[1] = '--help'
    main()


@main.command('version')
@click.pass_context
def main_version(ctx):
    """Print Streamlit's version number."""
    # Pretend user typed 'streamlit --version' instead of 'streamlit version'
    import sys
    assert len(sys.argv) == 2  # This is always true, but let's assert anyway.
    sys.argv[1] = '--version'
    main()


@main.command('docs')
def main_docs():
    """Show help in browser."""
    print('Showing help page in browser...')
    from streamlit import util
    util.open_browser('https://streamlit.io/secret/docs')


@main.command('hello')
def main_hello(args):
    """Runs the Hello World script."""
    print('Showing Hello World script in browser...')
    import streamlit.hello
    streamlit.hello.run()


@main.command('run')
@click.argument('file', type=click.Path(exists=True))
@click.argument('args', nargs=-1)
def main_run(file, args):
    """Run a Python script, piping stderr to Streamlit."""
    import streamlit.process_runner as process_runner
    import sys
    cmd = [sys.executable, file] + list(args)
    process_runner.run_handling_errors_in_this_process(cmd)


# DEPRECATED

@main.command('clear_cache', deprecated=True)
@click.pass_context
def main_clear_cache(ctx):
    """Deprecated."""
    click.echo(click.style('Use "cache clear" instead.', fg='red'))
    ctx.invoke(cache_clear)


@main.command('kill_proxy', deprecated=True)
@click.pass_context
def main_kill_proxy(ctx):
    """Deprecated."""
    click.echo(click.style('Use "proxy kill" instead.', fg='red'))
    ctx.invoke(proxy_kill)


@main.command('show_config', deprecated=True)
@click.pass_context
def main_show_config(ctx):
    """Deprecated."""
    click.echo(click.style('Use "config show" instead.', fg='red'))
    ctx.invoke(config_show)


# SUBCOMMAND: cache

@main.group('cache')
def cache():
    """Manage the Streamlit cache."""
    pass


@cache.command('clear')
def cache_clear():
    """Clear the Streamlit cache."""
    import streamlit.caching
    streamlit.caching.clear_cache(True)


# SUBCOMMAND: config

@main.group('config')
def config():
    """Manage Streamlit's config settings."""
    pass


@config.command('show')
def config_show():
    """Show all of Streamlit's config settings."""
    from streamlit import config
    config.show_config()


# SUBCOMMAND: proxy

@main.group('proxy')
def proxy():
    """Manage the Streamlit proxy."""
    pass


@proxy.command('kill')
def proxy_kill():
    """Kill the Streamlit proxy."""
    import psutil
    import getpass

    found_proxy = False

    for p in psutil.process_iter(attrs=['name', 'username']):
        # Attention: p.name() sometimes is 'python', sometimes 'Python', and
        # sometimes '/crazycondastuff/python'.
        try:
            if (('python' in p.name() or 'Python' in p.name())
                    and 'streamlit.proxy' in p.cmdline()
                    and getpass.getuser() == p.info['username']):
                print('Killing proxy with PID %d' % p.pid)
                p.kill()
                found_proxy = True
        # Ignore zombie process and proceses that have terminated
        # already.  ie you can't call process.name() on a process that
        # has terminated.
        except (psutil.ZombieProcess, psutil.NoSuchProcess):
            pass

    if not found_proxy:
        print('No Streamlit proxies found.')


if __name__ == '__main__':
    main()
