from UA2A import Seq2Seq
from torch.optim import Adam
from tqdm import tqdm
import os
import dataset
import config
import torch.nn.functional as F
import torch
import numpy as np
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from encoderCNN import ThreeD_conv


seq2seq_model = Seq2Seq().to(config.device)
optimizer = Adam(seq2seq_model.parameters(), lr=0.001)
if os.path.exists('./model/model.pkl'):
    seq2seq_model.load_state_dict(torch.load('./model/model.pkl'))
    optimizer.load_state_dict(torch.load('./model/optimizer.pkl'))

loss_list = []


def train(epoch):
    data_loader = dataset.get_dataloader(train=True)
    bar = tqdm(data_loader, total=len(data_loader), ascii=True, desc='train')
    for idx, (input_api, input_video, target, input_api_length, target_length) in enumerate(bar):
        input_api = input_api.to(config.device)
        target = target.to(config.device)
        input_api_length = input_api_length.to(config.device)

        decoder_ouputs, _ = seq2seq_model(input_api, input_api_length)

        decoder_ouputs = decoder_ouputs.view(-1, len(config.ns))
        target = target.view(-1)

        loss = F.nll_loss(decoder_ouputs, target, ignore_index=config.ns.PAD)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        loss_list.append(loss.item())

        bar.set_description("epoch:{} idx:{} loss:{:.3f}".format(epoch, idx, np.mean(loss_list)))
        if not (idx % 100):
            torch.save(seq2seq_model.state_dict(), './model/model.pkl')
            torch.save(optimizer.state_dict(), './model/optimizer.pkl')


if __name__ == '__main__':
    train(10)
    plt.figure(figsize=(50, 8))
    plt.plot(range(len(loss_list)), loss_list)
    plt.show()
