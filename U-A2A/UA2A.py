from encoderGRU import Encoder
from encoderCNN import ThreeD_conv
from decoder import Decoder
import torch.nn as nn
import torch

checkpoint = torch.load('3D-CNN.pkl')
state_dict = checkpoint['model']
CNN3D = ThreeD_conv()
CNN3D.load_state_dict(state_dict)
CNN3D.test()

class Seq2Seq(nn.Module):
    def __init__(self):
        super(Seq2Seq, self).__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, input_api, input_api_length, input_video, target):
        encoder_outputs, encoder_hidden = self.encoder(input_api, input_api_length)
        CNN_features = ThreeD_conv(input_video, 'test')
        fusion_features = torch.cat((CNN_features, encoder_hidden), 2)
        decoder_outputs, decoder_hidden = self.decoder(fusion_features, target)
        return decoder_outputs, decoder_hidden

    def evaluate(self, input_api, input_api_length, input_video):
        encoder_outputs, encoder_hidden = self.encoder(input_api, input_api_length)
        CNN_features = CNN3D(input_video, 'test')
        fusion_features = torch.cat((CNN_features, encoder_hidden), 2)
        decoder_outputs, decoder_predict = self.decoder.evaluate(fusion_features)
        return decoder_outputs, decoder_predict

    def evaluate_top_N(self, input_api, input_api_length, input_video, N):
        encoder_outputs, encoder_hidden = self.encoder(input_api, input_api_length)
        CNN_features = CNN3D(input_video, 'test')
        fusion_features = torch.cat((CNN_features, encoder_hidden), 2)
        decoder_predict = self.decoder.evaluate_top_n(fusion_features, N)
        return decoder_predict
