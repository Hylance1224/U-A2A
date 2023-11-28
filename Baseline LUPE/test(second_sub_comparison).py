import torch
from seq2seq import Seq2Seq
import config
import os
import numpy as np

test_path = 'G:/output_animation/test'

def calculate_acc():
    seq2seq_model = Seq2Seq().to(config.device)
    seq2seq_model.load_state_dict(torch.load('./model/seq2seq_model.pkl'))
    acc_list = []
    dirs = os.listdir(test_path)
    num = 0
    test_files = []
    for dir in dirs:
        path_animation = test_path + '/' + dir
        files = os.listdir(path_animation)
        for file in files:
            if 'animationApi' in file:
                test_files.append(path_animation + '/' + file)

    for f in test_files[0: 800]:

        f = open(f)
        api_list = f.readlines()
        num = num + 1
        numbering_api_list = config.dict.numbering_api(api_list)
        for i in range(1, len(numbering_api_list) - 1):
            split_point = i
            input_api = numbering_api_list[:split_point]
            output_api = numbering_api_list[split_point+1]
            input_length = torch.LongTensor([len(input_api)])
            input = torch.LongTensor(
                [config.ns.transform(input_api, max_len=config.training_len, add_sos=True, add_eos=True)])
            with torch.no_grad():
                hit = False
                input = input.to(config.device)
                input_length = input_length.to(config.device)
                predict = seq2seq_model.evaluate(input, input_length)
                decoder_predict = predict
                if output_api in decoder_predict:
                    hit = True

            if hit:
                acc_list.append(1)
            else:
                acc_list.append(0)
            print("{:.6f}".format(np.mean(acc_list_1)))


if __name__ == "__main__":
    calculate_acc_random()
