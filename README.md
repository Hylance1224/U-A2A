# U-A2A
Here is the relevant open-source code for the article titled “Which animation API should I use next? A multi-modal real-time animation API recommendation model for Android apps”

## Introduction
In this work, we designed and implemented a multi-modal model to provide the real-time animation API recommendation for developers of Android apps throughout the animation realization

## Environment
This tool is implemented in Python language, which can be run on Windows 11 with 2.4GHz core i7 CPU and 16 GB memory. 

## Functions
The relevant codes of our method include API recommendation model(U-A2A), UI animation collection (CollectingAnimation), mapping animation with corresponding API sequence (CollectingAPI), training 3D-CNN based animation feature extractor(Training-3DCNN). 

**1.   API recommendation model.** The code related to API recommendations is in the *U-A2A* folder. Users could execute the U-A2A by running the *recommendAPI.py*. To begin, provide the context of the code as well as the path of the UI animation that needs to be implemented, and the animation should be in GIF or video format. The output includes 10 APIs, which are the next possible APIs that may be used. The APIs at the top of the list have a higher probability of being utilized.

**2.   Animation collecting.** The code related to the animation collection is in the CollectingAnimation(Animation-ID) folder. The program requires the user to install and run the Android emulator before running. User could start to collect animation from apps by running *UiExploration.py*. 

**3.   Mapping animation to relevant API sequence.** The code is in the *CollectingAPI(API-ID)* folder. Users could map the collected animation to relevant API sequence by running *GetMappings.py*. 

**4.   Training animation feature extractor.** The code is in the *Training3D-CNN* folder. The architecture has two modules: an encoder, and a decoder. The encoder and decoder are built based on 3D-CNN model. By running main.py in the folder, you can generate a 3D-CNN animation feature extractor model file 3D-CNN.pkl. After moving the generated 3D-CNN.pkl to the U-A2A folder, it can be used to extract animation features in the API recommendation model.

## Data
The mapping relationships of UI animations and animation API sequences are available at https://1drv.ms/f/s!AhgAsR1GCvxgbSb_UpTNJ5b41lw?e=Oob8W

The APK files of apps are available at https://1drv.ms/f/s!AhgAsR1GCvxggR1i-JaP4NdnkgAk?e=7XROWQ

## How to replicate
**1. Data downloading and decompressing.** Download the data of mapping relationships between UI animations and animation API sequences, and then decompress the downloaded file. The decompressed file contains five folders: 1-fold, 2-fold, 3-fold, 4-fold, and 5-fold. Each folder corresponds to one fold of experimental data.

**2. The Model Training.** Create a *model* folder and a *train data* folder in *U-A2A* folder. Then, select 4 folds from the decompressed data (for example, you can select 1-fold, 2-fold, 3-fold, and 4-fold) and paste them into *train data* fold. Finally, run *train.py* in *U-A2A* fold to obtain the trained model. The trained model will be saved in *model* folder.

**3. Model Testing.** Create a *test data* folder and a *result* folder in *U-A2A* folder. Copy the remaining fold of the decompressed data into *test data* folder. Then, Run the *test_model.py* in *U-A2A* fold. The program will generate result documents in *result* folder. Each document stores a UI animation task, an animation API context, and the recommended animation APIs.

**4. Metric calculating.** Run the *calculate.py* in *U-A2A* fold. The program will generate the average accuracy results.


## Copyright
All copyright of the tool is owned by the author of the paper.


