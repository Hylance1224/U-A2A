import torch
from UA2A import Seq2Seq
import config

input_api_sequence = []
numbering_api_list = config.dict.numbering_api(input_api_sequence)
animation_path = ''
seq2seq_model = Seq2Seq().to(config.device)
seq2seq_model.load_state_dict(torch.load('./U-A2A/model.pkl'))
input_length = torch.LongTensor([len(input_api_sequence)])
input = torch.LongTensor([config.ns.transform(numbering_api_list, max_len=config.training_len, add_sos=True, add_eos=True)])
with torch.no_grad():
    input = input.to(config.device)
    input_length = input_length.to(config.device)
    predict = seq2seq_model.evaluate_top_n(input, input_length, animation_path, 10)
    predict_api = config.dict.api_numbering(predict)
    print(predict_api)