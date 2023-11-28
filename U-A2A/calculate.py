import torch
from UA2A import Seq2Seq
import config
import os
import numpy as np

test_path = '.test'

def calculate_acc():
    seq2seq_model = Seq2Seq().to(config.device)
    seq2seq_model.load_state_dict(torch.load('./model/model.pkl'))
    acc_list_1 = []
    acc_list_3 = []
    acc_list_5 = []
    acc_list_10 = []
    dirs = os.listdir(test_path)
    num = 0
    test_files = []
    for dir in dirs:
        path_animation = test_path + '/' + dir
        files = os.listdir(path_animation)
        for file in files:
            if 'animationApi' in file:
                test_files.append(path_animation + '/' + file)

    for f in test_files:
        hit_1 = False
        hit_3 = False
        hit_5 = False
        hit_10 = False
        f = open(f)
        api_list = f.readlines()
        num = num + 1
        numbering_api_list = config.dict.numbering_api(api_list)
        length = len(numbering_api_list)
        end = length-1
        start = 2
        for i in range(start, end):
            split_point = i
            input_api = numbering_api_list[:split_point]
            output_api = numbering_api_list[split_point:split_point + config.testing_len]
            input_length = torch.LongTensor([len(input_api)])
            input = torch.LongTensor(
                [config.ns.transform(input_api, max_len=config.training_len, add_sos=True, add_eos=True)])
            with torch.no_grad():
                input = input.to(config.device)
                input_length = input_length.to(config.device)
                decoder_predict = seq2seq_model.evaluate_top_n(input, input_length, 10)
                decoder_predict_1 = decoder_predict[:1]
                decoder_predict_3 = decoder_predict[:3]
                decoder_predict_5 = decoder_predict[:5]
                decoder_predict_10 = decoder_predict[:10]

                if output_api[0] in decoder_predict_1:
                    hit_1 = True
                if output_api[0] in decoder_predict_3:
                    hit_3 = True
                if output_api[0] in decoder_predict_5:
                    hit_5 = True
                if output_api[0] in decoder_predict_10:
                    hit_10 = True

        if hit_1:
            acc_list_1.append(1)
        else:
            acc_list_1.append(0)
        if hit_3:
            acc_list_3.append(1)
        else:
            acc_list_3.append(0)
        if hit_5:
            acc_list_5.append(1)
        else:
            acc_list_5.append(0)
        if hit_10:
            acc_list_10.append(1)
        else:
            acc_list_10.append(0)


        print("{:.6f}".format(np.mean(acc_list_1)))
        print("{:.6f}".format(np.mean(acc_list_3)))
        print("{:.6f}".format(np.mean(acc_list_5)))
        print("{:.6f}".format(np.mean(acc_list_10)))



if __name__ == "__main__":
    calculate_acc()
