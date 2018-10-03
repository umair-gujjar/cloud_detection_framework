import argparse
import os
import convert_to_yolo_format
import shutil


parser = argparse.ArgumentParser(description='Input path to darknet')
parser.add_argument('DARKNET_PATH', type=str, nargs=1,
                    help='Set path to darknet')
parser.add_argument('DATA_PATH', type=str, nargs=1,
                    help='Set path to data folder, containg datasets')

args = parser.parse_args()
DARKNET_PATH = args.DARKNET_PATH[0]
DATA_PATH = args.DATA_PATH[0]


def set_training_datasets():
    try:
        datasets = os.listdir(DATA_PATH)
    except Exception as e:
        print 'No folder named ~/data'
        print 'Exception: ', e
    if len(datasets) == 0:
        print 'No datasets in ~/data, run config_new_dataset.py on your dataset and move the dataset folder to ~/data'

    for i in range(0, len(datasets)):
        print '[', i, ']', datasets[i]
    user_input = str(raw_input(
        'Input the number for the datasets you wish to train on, separate numbers with space: ')).split()
    training_dataset_paths = []
    for dataset_index in user_input:
        training_dataset_paths.append(
            os.path.join(DATA_PATH, datasets[int(dataset_index)]))
    return training_dataset_paths


def setup_tmp_folder():
    tmp_folder_path = os.path.join(DATA_PATH, 'tmp')
    tmp_folder_test_path = os.path.join(tmp_folder_path, 'test')
    tmp_folder_train_path = os.path.join(tmp_folder_path, 'train')
    if os.path.exists(tmp_folder_path):
        shutil.rmtree(tmp_folder_path, ignore_errors=True)
    os.makedirs(tmp_folder_path)
    os.makedirs(tmp_folder_test_path)
    os.makedirs(tmp_folder_train_path)
    return [tmp_folder_path, tmp_folder_train_path, tmp_folder_test_path]


def generate_yolo_train_files():
    training_dataset_paths = set_training_datasets()
    [tmp_folder_path, tmp_folder_train_path, tmp_folder_test_path] = setup_tmp_folder()
    train_txt = open(os.path.join(tmp_folder_path, 'train.txt'), 'w')
    test_txt = open(os.path.join(tmp_folder_path, 'test.txt'), 'w')
    for training_dataset in training_dataset_paths:
        for filename in os.listdir(os.path.join(training_dataset, 'train')):
            shutil.copy2(os.path.join(training_dataset, 'train',
                                      filename), tmp_folder_train_path)
            shutil.copy2(os.path.join(training_dataset, 'train',
                                      filename[:-4] + '.xml'), tmp_folder_train_path)
            if filename.endswith('.jpg'):
                train_txt.write(os.path.join(tmp_folder_train_path, filename) + '\n')
        for filename in os.listdir(os.path.join(training_dataset, 'test')):
            shutil.copy2(
                os.path.join(training_dataset, 'test', filename), tmp_folder_test_path)
            shutil.copy2(os.path.join(training_dataset, 'test',
                                      filename[:-4] + '.xml'), tmp_folder_test_path)
            if filename.endswith('.jpg'):
                test_txt.write(os.path.join(tmp_folder_test_path, filename) + '\n')
    test_txt.close()
    train_txt.close()
    classes = convert_to_yolo_format.get_classes(
        [tmp_folder_test_path, tmp_folder_train_path])
    convert_to_yolo_format.generate_yolo_annotation_files(
        tmp_folder_train_path, classes)
    convert_to_yolo_format.generate_yolo_annotation_files(
        tmp_folder_test_path, classes)
    convert_to_yolo_format.generate_classes_file(tmp_folder_path, classes)
    # CFG
    # OBJ.Names obj.data in darknet/data
    # Set Batch and subdivisions in CFG
    # Set classes in CFG, line 620, 696, 783
    # set Filters (classes + 5) * 3 in CFG, line 602, 689, 776
    # weights saved every 1000 iteration


if __name__ == '__main__':
    generate_yolo_train_files()
