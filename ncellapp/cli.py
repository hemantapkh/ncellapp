from .ncellapp import register as register_ncell
from .ncellapp import ncell
import click

print("""
    _   _          _ _    _                   ____ _     ___ 
    | \ | | ___ ___| | |  / \   _ __  _ __    / ___| |   |_ _|
    |  \| |/ __/ _ \ | | / _ \ | '_ \| '_ \  | |   | |    | | 
    | |\  | (_|  __/ | |/ ___ \| |_) | |_) | | |___| |___ | | 
    |_| \_|\___\___|_|_/_/   \_\ .__/| .__/   \____|_____|___|
                                |_|   |_|                      
    """)


def error(text):
    return click.style(f"\n--- {text} ---\n", fg="red")


def success(text):
    return click.style(f"\n--- {text} ---\n", fg="green")


@click.group()
@click.pass_context
@click.option('--phonenumber', '-pn', type=int, help="Pass your phone number.")
@click.option('--token', '-t', type=str, help="Pass token you got from register.")
def main(ctx, phonenumber, token):
    ctx.ensure_object(dict)
    ctx.obj['number'] = phonenumber
    ctx.obj['token'] = token


@main.command()
@click.pass_context
def register(ctx):
    ''' Gives you token to use this app features.'''
    number = ctx.obj['number']
    if not number:
        click.echo(
            error('No Phone number passed. Pass it using -pn [your number] or type --help for help'))
    elif len(str(number)) is not 10:
        click.echo(error(
            'Invalid phone number. For help type --help'))
    else:
        reg = register_ncell(str(number))
        resp = reg.sendOtp()
        if resp['opStatus'] != "12":
            click.echo(resp['errorMessage'])
        else:
            click.echo('Code is sent to your phone.')
            code = click.prompt('Enter OTP you received', type=int)
            token = reg.getToken(code)
            if 'token' not in token:
                click.echo(error('Invalid OTP.'))
            else:
                print(
                    success(f"Your token is \n{token['token']}\n save it somewhere you will need it next time you use this cli."))


def checkToken(token):
    account = ncell(token)
    data = account.login()
    if data['opStatus'] == 'invalid':
        print(
            error('Invalid token. Pass it using -t [token] or type --help for help.'))
        return None
    else:
        return account


@main.command()
@click.pass_context
def view_profile(ctx):
    ''' List your profile data  '''
    code = ctx.obj['token']
    loggedUser = checkToken(code)
    if loggedUser:
        loggedUser.viewProfile()
        print('\n--- ACCOUNT INFORMATION ---\n')
        print(f" Owner Name : {loggedUser.name}\n")
        print(f" Current Plan : {loggedUser.currentPlan}\n")
        print(f" Phone Number : {loggedUser.msidn}\n")
        print("---------\n")


@main.command()
@click.pass_context
@click.option('--destination', '-d', prompt="Enter destination number", type=int, required=True, help="Destination number.")
@click.option('--message', '-m', prompt="Enter your sms message", type=str, required=True, help="Contents of sms.")
@click.option('--schedule', '-s', prompt="Enter Schedule of message (Format: YYYYMMDDHHMMSS), eg.20201105124500 or type - for no schedule", type=str, required=False, help="Schedule of message (Format: YYYYMMDDHHMMSS), eg.20201105124500.")
def sendPaidSms(ctx, destination, message, schedule):
    ''' Send a paid sms  '''
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        if len(str(destination)) != 10:
            click.echo(error('Invalid destination number.'))
        else:
            schedule = schedule if schedule != "-" else None
            data = loggedUser.sendSms(destination, message, schedule)
            if data['opStatus'] == '3':
                click.echo(data['errorMessage'])
            else:
                click.echo(success(f'Message sent to : {destination}'))


@main.command()
@click.pass_context
@click.option('--destination', '-d', prompt="Enter destination number", type=int, required=True, help="Destination number.")
@click.option('--message', '-m', prompt="Enter your sms message", type=str, required=True, help="Contents of sms.")
@click.option('--schedule', '-s', prompt="Enter Schedule of message (Format: YYYYMMDDHHMMSS), eg.20201105124500 or type - for no schedule", type=str, required=False, help="Schedule of message (Format: YYYYMMDDHHMMSS), eg.20201105124500.")
def sendFreeSms(ctx, destination, message, schedule):
    ''' Send a paid sms  '''
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        if len(str(destination)) != 10:
            click.echo(error('Invalid destination number.'))
        else:
            schedule = schedule if schedule != "-" else None
            data = loggedUser.sendFreeSms(destination, message, schedule)
            if data['opStatus'] == '3':
                click.echo(data['errorMessage'])
            else:
                click.echo(success(f'Message sent to : {destination}'))


@main.command()
@click.pass_context
def getBalance(ctx):
    """ Get your account balance """
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        balance = loggedUser.viewBalance()['prePaid']
        click.echo(success(
            f'You have Rs.{balance["balance"]} in your account.'))


@main.command()
@click.pass_context
@click.option('--pin', '-rpin', prompt="Enter Recharge Pin [16 digits]", type=int, required=True, help="Recharge pin.")
def recharge(ctx, pin):
    """ Get your account balance """
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        balance = loggedUser.selfRecharge(pin)
        if 'srRefNumber' in balance:
            click.echo("\n--- "+balance['srRefNumber']+"\n--- ")
        else:
            click.echo("\n --- Recharge Successfull. --- \n")


@main.command()
@click.pass_context
@click.option('--pin', '-rpin', prompt="Enter Recharge Pin [16 digits]", type=int, required=True, help="Recharge pin.")
@click.option('--destination', '-dn', prompt="Enter Destination number", type=int, required=True, help="Destination number.")
def rechargeOthers(ctx, pin, destination):
    """ Get your account balance """
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        balance = loggedUser.recharge(destination, pin)
        if 'srRefNumber' in balance:
            click.echo("\n--- "+balance['srRefNumber']+"\n--- ")
        else:
            click.echo("\n--- Recharge Successfull. ---\n")


@main.command()
@click.pass_context
def rechargeHistory(ctx):
    """ Get your account balance """
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        history = loggedUser.rechargeHistory()
        if history['opStatus'] == '9':
            click.echo(error(history['errorMessage']))
        else:
            click.echo('\n--- Transfer History ---\n')
            click.echo(
                f'--- Amount: {history["rechargeHistory"]["mrp"]} ---\n')
            click.echo(
                f'--- To: {history["rechargeHistory"]["expiryDate"]} ---\n')


@main.command()
@click.pass_context
@click.option('--amount', '-amt', prompt="Enter amount to send", type=int, required=True, help="Amount to send.")
@click.option('--destination', '-dn', prompt="Enter Destination number", type=int, required=True, help="Destination number.")
def transferBalance(ctx, amount, destination):
    """ Get your account balance """
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        balance = loggedUser.balanceTransfer(destination, amount)
        otp = click.prompt('Enter otp received', type=int)
        resp = loggedUser.confirmBalanceTransfer(otp)
        click.echo(f'\n--- {resp["srRefNumber"]} ---\n')


@main.command()
@click.pass_context
@click.option('--amount', '-amt', prompt="Enter amount to send", type=int, required=True, help="Amount to send.")
@click.option('--destination', '-dn', prompt="Enter Destination number", type=int, required=True, help="Destination number.")
def transferBalance(ctx, amount, destination):
    """ Get your account balance """
    loggedUser = checkToken(ctx.obj['token'])
    if loggedUser:
        balance = loggedUser.balanceTransfer(destination, amount)
        otp = click.prompt('Enter otp received', type=int)
        resp = loggedUser.confirmBalanceTransfer(otp)
        click.echo(f'\n--- {resp["srRefNumber"]} ---\n')
