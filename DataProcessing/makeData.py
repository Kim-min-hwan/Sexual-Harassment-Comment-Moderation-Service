import os
import shutil
import pandas as pd
import numpy as np
from glob import glob
from sklearn.model_selection import train_test_split

class makeData:
    def __init__(self, data_dir, data_file, date='', dev_size=0.22, test_size=0.11):
        self.data_path = data_dir + '/' + data_file
        self.df = pd.read_csv(self.data_path, sep='\t')
        self.date = '_' + date if date != '' else date

        self.split_train_valid_and_test(dev_size, test_size)
        self.save_to_csv(data_dir)

    def split_train_valid_and_test(self, dev_size, test_size):
        label = 'bias'
        self.df_train, self.df_test = train_test_split(self.df, test_size=dev_size+test_size, stratify=self.df[label], random_state=42)
        self.df_test, self.df_dev = train_test_split(self.df_test, test_size=dev_size/(dev_size+test_size), stratify=self.df_test[label], random_state=42)

        self.df_test_gt = self.df_test[[label, 'hate']]
        self.df_test = self.df_test[['title', 'comment']]


    def save_to_csv(self, save_dir):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        self.df_train.to_csv(os.path.join(save_dir, f'train.txt'), sep='\t', index=False)
        self.df_dev.to_csv(os.path.join(save_dir, f'validate.txt'), sep='\t', index=False)
        self.df_test.to_csv(os.path.join(save_dir, f'test.txt'), sep='\t', index=False)
        self.df_test_gt.to_csv(os.path.join(save_dir, f'test_gt.txt'), sep='\t', index=False)

if __name__ == '__main__':
    data_dir_path = './Data'
    data_filename = 'total.txt'
    makeData(data_dir_path, data_filename)