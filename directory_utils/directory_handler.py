import os


def is_not_directory(folder_path):
    return False if os.path.isdir(folder_path) else True


def getting_parent_directory(folder_path):
    return '/'.join(folder_path.split('/')[:-1])


def count_dcm_files(folder_path):
    return len([f for f in os.listdir(folder_path) if f.endswith(".dcm")])


def count_nii_files(folder_path):
    return len([f for f in os.listdir(folder_path) if f.endswith(".nii") or f.endswith(".nii.gz")])


def getting_files_directories_path(file_directory):
    file_paths = {}
    for file in os.listdir(file_directory):
        if 'flair.nii' in file:
            file_paths['flair'] = os.path.join(file_directory, file)
        elif 't1.nii' in file:
            file_paths['t1'] = os.path.join(file_directory, file)
        elif 't1ce.nii' in file:
            file_paths['t1ce'] = os.path.join(file_directory, file)
        elif 't2.nii' in file:
            file_paths['t2'] = os.path.join(file_directory, file)
        elif 'seg.nii' in file:
            file_paths['seg'] = os.path.join(file_directory, file)
    return file_paths
