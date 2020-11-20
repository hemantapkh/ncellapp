from .ncellapp import register as register_ncell
from .ncellapp import ncell
import click


@click.group()
def main():
    ''' NcellApp description here '''


@main.command()
@click.option('--number', prompt='Your Phone Number', type=int, required=True, help='Type your phone number')
def register(number):
    ''' Register'''
    if len(str(number)) is not 10:
        click.echo('Invalid phone number.')
    else:
        reg = register_ncell(number)
        reg.sendOtp()
        # click.echo('Code is sent to your phone.')
        # code = click.prompt('Enter OTP you received', type=int)
        token = reg.getToken(123)


@main.command()
@click.option('--code', prompt="Enter the code you received", type=int, required=True, help='Pass your token which you got in sms')
def login(code):
    ''' Login  '''
    account = ncell(code)
