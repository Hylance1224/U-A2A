import torch
from UA2A import Seq2Seq
import config
import os
import numpy as np

test_path = '.test data'
result_path = '.result'

def recommend_api():
    seq2seq_model = Seq2Seq().to(config.device)
    seq2seq_model.load_state_dict(torch.load('./model/model.pkl'))
    dirs = os.listdir(test_path)
    num = 0
    test_files = []
    for dir in dirs:
        path_animation = test_path + '/' + dir
        files = os.listdir(path_animation)
        for file in files:
            if 'animationApi' in file:
                test_files.append(path_animation + '/' + file)

    result_number = 0
    for f in test_files:
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
                decoder_predict_10 = decoder_predict[:10]

                input_api = config.dict.number_to_api(input_api)
                output_api = config.dict.number_to_api(decoder_predict_10)
                animation_name = f
                result_f = open(result_path + '/' + str(result_number) + '.txt', 'w')
                result_f.write('Input animation:')
                result_f.write(animation_name)
                result_f.write('\n')
                result_f.write('Input API sequence:')
                result_f.write(input_api)
                result_f.write('\n')
                result_f.write('Output API:')
                result_f.write(output_api)
                result_f.write('\n')
                result_f.close()



if __name__ == "__main__":
    recommend_api()
