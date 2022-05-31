import re
import os
import subprocess as sp
import yaml

from numpy import mat

DEST_YAML = 'clients-auto.yml'
SRC_CSV = 'Groups.csv'
CLONE_DIR = 'clients-test'
NOTE_CSV = 'notes-auto.csv'

# csv format
# nom IA;étudiants;lien github
# Bot-4000;Quentin Lurkin (LUR), André Lorge (LRG);https://github.com/qlurkin/PI2CChampionshipRunner

studentPattern = re.compile(r'(.+) \((.+)\)')

def loadCSV():
    with open(SRC_CSV, encoding='utf8') as file:
        clients = []
        file.readline()
        for i, line in enumerate(file):
            port = 4000 + i
            iaName, studentStrings, gitLink = line.strip().split(';')
            gitDir = gitLink[gitLink.rindex('/')+1:]
            if gitDir.endswith('.git'):
                gitDir = gitDir[:-4]
            students = []
            for student in studentStrings.split(', '):
                match = studentPattern.match(student)
                if match is None:
                    print('Unable to parse student:', student)
                    continue
                students.append({
                    'name': match.group(1),
                    'matricule': match.group(2)
                })
            studentDir = os.path.join(CLONE_DIR, str(port))
            # if not os.path.exists(studentDir):
            #     os.mkdir(studentDir)
            #     sp.run(['git', 'clone', gitLink], cwd=studentDir)
            clients.append({
                'name': iaName,
                'students': students,
                'cwd': os.path.join(studentDir, gitDir),
                'cmd': '',
                'git': gitLink,
                'port': port,
            })

    return clients

def create_clone_dir():
    if not os.path.exists(CLONE_DIR):
        os.makedirs(CLONE_DIR)

def saveYaml(clients):
    with open(DEST_YAML, 'w', encoding='utf8') as file:
        file.write(yaml.dump(clients, allow_unicode=True))

def save_notes_csv(clients):
    with open(NOTE_CSV, 'w', encoding='utf8') as file:
        for client in clients:
            for student in client['students']:
                file.write('{ia};{name};{matricule}\n'.format(
                    ia=client['name'],
                    name=student['name'],
                    matricule=student['matricule']
                ))



if __name__ == '__main__':
    create_clone_dir()
    clients = loadCSV()
    saveYaml(clients)
    save_notes_csv(clients)