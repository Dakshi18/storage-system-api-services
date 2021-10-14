import os
import shutil
from cryptography.fernet import Fernet


def copy_file(file_pattern, count):
        total_count_replicas = len(os.listdir('data'))
        if total_count_replicas != 0:
                new_replicas_count = total_count_replicas + count
                i = total_count_replicas + 1
                while i <= new_replicas_count:
                        print(file_pattern + str(i))
                        # instead of 1st replica , we can take from latest updates replica
                        shutil.copytree(file_pattern + str(1), file_pattern + str(i))
                        i += 1
        else:
                # When there is no replica available, the data should be fetched from the backup and replicates it 
                i=1
                while i <= count:
                        print(file_pattern + str(i))
                        shutil.copytree('./backup/replica-' + str(1), file_pattern + str(i))
                        i += 1

def generate_encryption_key():
    return Fernet.generate_key()


