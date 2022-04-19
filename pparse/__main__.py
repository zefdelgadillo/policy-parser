#!/usr/bin/env python
import click
from pparse.policy import Policy
from pparse.iam import Role, AuthenticationError
import sys
import yaml
import json
import io
import csv
from tabulate import tabulate
import logging

GLOBAL_OPTIONS = {}
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)


@click.group(invoke_without_command=True)
@click.option(
    "-f",
    "--input-file",
    help="Filename of the IAM policy, omit to read from stdin.",
    type=click.File("r"),
    default=sys.stdin,
)
@click.option(
    "-i",
    "--input-format",
    help="Input format of policy document to parse.",
    type=click.Choice(['yaml', 'json'], case_sensitive=False),
    default="yaml",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format for the parsed policy.",
    type=click.Choice(['yaml', 'json', 'csv', 'table'], case_sensitive=False),
    default="yaml",
)
@click.option('-v', '--verbose', count=True)
def cli(input_file, input_format, output_format, verbose):
    """Parse and filter Google Cloud Platform IAM policy documents."""
    set_logger(verbose)
    ctx = click.get_current_context()
    validate_or_show_help(
        input_file.isatty())  # Make sure STDIN has data, otherwise show help
    if input_format == 'json':
        policy_dict = json.loads(input_file.read())
    elif input_format == 'yaml':
        policy_dict = yaml.safe_load(input_file.read())
    GLOBAL_OPTIONS['policy'] = Policy().from_dict(policy_dict)
    GLOBAL_OPTIONS['output_format'] = output_format
    if ctx.invoked_subcommand is None:
        click.echo(
            policy_formatter(GLOBAL_OPTIONS['policy'],
                             GLOBAL_OPTIONS['output_format']))


@cli.command()
@click.option(
    "-s",
    "--roles-only",
    help="Only show list of roles.",
    is_flag=True,
    default=False,
)
@click.argument('principal', nargs=-1)
def principal(principal, roles_only):
    """Filter results based on user principal.
    
    Pass in one or more USER/PRINCIPAL email addresses to receive list of roles associated with those users"""
    principal_list = list(principal)
    validate_or_show_help(len(principal_list) == 0)
    policy = GLOBAL_OPTIONS['policy']
    policy.filter_bindings_by_principals(principal_list)
    if roles_only == False:
        click.echo(policy_formatter(policy, GLOBAL_OPTIONS['output_format']))
    else:
        click.echo("\n".join(policy.roles()))


@cli.command()
@click.argument('role', nargs=-1)
@click.option(
    "-s",
    "--users-only",
    help="Only show list of users.",
    is_flag=True,
    default=False,
)
def role(role, users_only):
    """Filter results based on role.
    
    Pass in one or more ROLE names to receive list of users with that binding"""
    role_list = list(role)
    validate_or_show_help(len(role_list) == 0 and users_only == False)
    policy = GLOBAL_OPTIONS['policy']
    policy.filter_bindings_by_roles(role_list)
    if users_only == False:
        click.echo(policy_formatter(policy, GLOBAL_OPTIONS['output_format']))
    else:
        click.echo("\n".join(sorted(policy.principals())))


@cli.command()
@click.argument('domain')
def domain(domain):
    """Filter results based on domain.
    
    Pass in a DOMAIN to receive list of associated bindings"""
    policy = GLOBAL_OPTIONS['policy']
    policy.filter_bindings_by_domain(domain)
    click.echo(policy_formatter(policy, GLOBAL_OPTIONS['output_format']))


@cli.command()
@click.argument('type')
def type(type):
    """Filter results based on principal type.
    
    Pass in a TYPE (serviceAccount, user, group) to receive list of associated bindings."""
    if type.lower() not in ['user', 'serviceaccount', 'domain', 'group']:
        click.BadArgumentUsage(
            'Type must be one of user, serviceaccount, domain, or group')
    policy = GLOBAL_OPTIONS['policy']
    policy.filter_bindings_by_type(type)
    click.echo(policy_formatter(policy, GLOBAL_OPTIONS['output_format']))


@cli.command()
@click.argument('permission')
@click.option(
    "-r",
    "--roles-only",
    help="Only show list of roles.",
    is_flag=True,
    default=False,
)
@click.option(
    "-u",
    "--users-only",
    help="Only show list of roles.",
    is_flag=True,
    default=False,
)
def permission(permission, roles_only, users_only):
    """Filter results based on permission.
    
    Pass in a PERMISSION to receive list of associated bindings."""
    policy = GLOBAL_OPTIONS['policy']
    roles_list = list(policy.roles())
    try:
        matching_roles = Role(roles_list, permission).matching_roles()
        policy.filter_bindings_by_roles(matching_roles)
        if roles_only == False and users_only == False:
            click.echo(
                policy_formatter(policy, GLOBAL_OPTIONS['output_format']))
        elif roles_only == True:
            click.echo("\n".join(sorted(policy.roles())))
        elif users_only == True:
            click.echo("\n".join(sorted(policy.principals())))
    except AuthenticationError as e:
        raise click.ClickException(e)


cli.add_command(principal)
cli.add_command(role)
cli.add_command(domain)
cli.add_command(type)
cli.add_command(permission)


def policy_formatter(policy, style):
    if style == 'yaml':
        return yaml.dump(policy.to_dict())
    elif style == 'json':
        return json.dumps(policy.to_dict())
    elif style == 'csv':
        return csv_writer(policy.to_list())
    elif style == 'table':
        return tabulate(policy.to_list(), headers="keys")
    else:
        return policy.to_dict()


def set_logger(verbose):
    level = logging.WARN
    if verbose == 0:
        level = logging.WARN
    if verbose == 1:
        level = logging.INFO
    if verbose == 2:
        level = logging.DEBUG
    logging.getLogger().setLevel(level=level)


def validate_or_show_help(validation, true_false=True):
    ctx = click.get_current_context()
    if (validation == true_false):
        click.echo(ctx.get_help())
        ctx.exit()


def csv_writer(list_data, delimiter=',', headers=[]):
    headers = list(list_data[0].keys()) if headers == [] else headers
    output = io.StringIO()
    writer = csv.DictWriter(output,
                            fieldnames=headers,
                            delimiter=delimiter,
                            quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(list_data)
    return output.getvalue()


if __name__ == '__main__':
    cli()
