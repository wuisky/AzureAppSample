# apt install ansible dmidecode
# pip install ansible-runner
# sudo apt install ssh git connect-proxy python3-jinja2
# ssh-keygen -t rsa -m PEM
# ssh-copy-id localhost
import argparse
import os
import ansible_runner


def run_playbook():
    parser = argparse.ArgumentParser(
        description='start ansible'
    )

    parser.add_argument(
        '-p', '--password',
        help='ubuntu user password.',
        type=str,
        default='ubuntu',
    )

    parser.add_argument(
        '-g', '--gpu',
        help='use gpu or not.',
        type=str,
        default='false',
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    playbook_path = 'playbooks/rp2-deploy.yml'
    inventory = 'localhost'
    extra_vars = {
        'ansible_user': os.getenv('USER'),
        'ansible_become_password': args.password,
        'gpu': args.gpu,
    }

    r = ansible_runner.run(
        private_data_dir='.',  # current directory, can be adjusted as needed
        playbook=playbook_path,
        inventory=inventory,
        extravars=extra_vars,
        verbosity=2,  # equivalent to -vv
        # roles_path=None,
    )

    print(f"Status: {r.status}")
    print(f"RC: {r.rc}")

    for event in r.events:
        print(event['stdout'])


if __name__ == "__main__":
    run_playbook()
