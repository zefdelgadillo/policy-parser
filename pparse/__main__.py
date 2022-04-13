#!/usr/bin/env python
import click
from pparse.policy import Policy
import sys
import yaml
import json
import io
import csv
from tabulate import tabulate

GLOBAL_OPTIONS = {}


@click.group(invoke_without_command=True)
@click.option(
    "-f",
    "--input-file",
    help="Filename of the IAM policy, omit to read from STDIN.",
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
def cli(input_file, input_format, output_format):
    """Parse and filter Google Cloud Platform IAM policy documents."""
    ctx = click.get_current_context()
    if (input_file.isatty()):
        click.echo(ctx.get_help())
        ctx.exit()
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
@click.argument('principal')
def principal(principal, roles_only):
    """Filter results based on user principal.
    
    Pass in a USER/PRINCIPAL to receive list of roles associated with that user"""
    policy = GLOBAL_OPTIONS['policy']
    policy.filter_bindings_by_principal(principal)
    if roles_only == False:
        click.echo(policy_formatter(policy, GLOBAL_OPTIONS['output_format']))
    else:
        click.echo("\n".join(policy.roles()))


@cli.command()
@click.argument('role')
@click.option(
    "-s",
    "--users-only",
    help="Only show list of users.",
    is_flag=True,
    default=False,
)
def role(role, users_only):
    """Filter results based on role.
    
    Pass in a ROLE to receive list of users with that binding"""
    policy = GLOBAL_OPTIONS['policy']
    policy.filter_bindings_by_role(role)
    if users_only == False:
        click.echo(policy_formatter(policy, GLOBAL_OPTIONS['output_format']))
    else:
        click.echo("\n".join(policy.principals()))


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


cli.add_command(principal)
cli.add_command(role)
cli.add_command(domain)
cli.add_command(type)


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
