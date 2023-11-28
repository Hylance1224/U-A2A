import os

import numpy as np
import torch
from torch import nn
from torch.autograd import Variable
from torchvision import transforms
from PIL import Image
from PIL import ImageSequence
import numpy

from lib import ParseGRU,Visualizer
from network import ThreeD_conv


def transform(video):
    trans_video = torch.empty(opt.n_channels,opt.T,opt.image_height,opt.image_width)
    for i in range(opt.T):
        img = video[:,i]
        img = trans(img).reshape(opt.n_channels,opt.image_height,opt.image_width)
        trans_video[:,i] = img
    return trans_video


def trim(video):
    start = np.random.randint(0, video.shape[1] - (opt.T+1))
    end = start + opt.T
    return video[:, start:end, :, :]


def random_choice(n_videos, files):
    X = []
    for _ in range(opt.batch_size):
        file = files[np.random.randint(0, n_videos-1)]
        video = read_gif(file)
        while video is None:
            file = files[np.random.randint(0, n_videos - 1)]
            video = read_gif(file)
        video = video.transpose(3, 0, 1, 2) / 255.0
        video = torch.Tensor(video)
        video = transform(video)
        X.append(video)
    X = torch.stack(X)
    return X


def get_gif(path):
    gifs = []
    files = os.listdir(path)
    for file in files:
        if os.path.isdir(path+'/'+file):
            gifs.extend(get_gif(path+'/'+file))
        else:
            gifs.append(path+'/'+file)
    return gifs


def read_gifs(files):
    videos = []
    for file in files:
        img = Image.open(file)
        a_frames = []
        i = 1
        final_frame = None
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert('RGB')
            a_frames.append(numpy.asarray(frame))
            final_frame = frame
            if i >= opt.frame:
                break
            i = i + 1
        if i < opt.frame:
            for w in range(opt.frame - i + 1):
                a_frames.append(final_frame)
        try:
            a = numpy.stack(a_frames)
        except:
            pass
        if a.shape == (16, 500, 281, 3):
            videos.append(a)
    return videos


def read_gif(file):
    img = Image.open(file)
    a_frames = []
    i = 1
    final_frame = None
    for frame in ImageSequence.Iterator(img):
        frame = frame.convert('RGB')
        a_frames.append(numpy.asarray(frame))
        final_frame = frame
        if i >= opt.frame:
            break
        i = i + 1
    if i < opt.frame:
        for w in range(opt.frame - i + 1):
            a_frames.append(final_frame)
    try:
        a = numpy.stack(a_frames)
    except:
        return None
    if a.shape == (16, 500, 281, 3):
        return a
    return None


if __name__ == '__main__':
    parse = ParseGRU()
    opt = parse.args
    autoencoder = ThreeD_conv(opt)
    autoencoder.train()
    mse_loss = nn.MSELoss()
    optimizer = torch.optim.Adam(autoencoder.parameters(),
                                 lr=opt.learning_rate,
                                 weight_decay=1e-5)

    files = get_gif("G:/animations")

    n_videos = len(files)
    print(n_videos)
    if opt.cuda:
        autoencoder.cuda()
    trans = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Grayscale(1),
        transforms.Resize((opt.image_height, opt.image_width)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])

    losses = np.zeros(opt.n_itrs)
    visual = Visualizer(opt)

    for itr in range(opt.n_itrs):
        real_videos = random_choice(n_videos, files)
        x = real_videos
        if opt.cuda:
            x = Variable(x).cuda()
        else:
            x = Variable(x)

        xhat = autoencoder(x)
        loss = mse_loss(xhat, x)
        losses[itr] = losses[itr] * (itr / (itr + 1.)) + loss.data * (1. / (itr + 1.))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print('itr [{}/{}], loss: {:.4f}'.format(
            itr + 1,
            opt.n_itrs,
            loss))
        visual.losses = losses
        visual.plot_loss()
        if itr % 2000 == 0:
            state = {'model': autoencoder.state_dict(), 'optimizer': optimizer.state_dict()}
            torch.save(state, '3D-CNN.pkl')