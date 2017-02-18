import numpy as np
import cnn_lstm
from scipy.misc import imread, imresize
from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, AveragePooling2D, ZeroPadding2D, Dropout, Flatten, merge, Reshape, Activation
from keras.models import Model
from keras.regularizers import l2
from keras.optimizers import SGD
from custom_layers import PoolHelper  # ,LRN
#import caffe
import cv2
import utilities
from LRN2D import LRN2D as LRN
import settings
from similarityMeasures import getError
directory = settings.directory  # "/usr/prakt/w065/posenet/sm/"
datasource = utilities.get_data(settings.testsetpath)
datagen = utilities.gen_data(datasource)
#outputDirectory = "/usr/prakt/w065/posenet/TFData/"
#meanFileLocation = 'smmean.binaryproto'
# 'tfsmtrainedweights.h5'#'75batbhessmtrainedweights.h5'#'smtrainedweights.h5'
weightsfile = settings.outputWeightspath
# weightsfile='shoptrainedweights.h5'
poses = []  # will contain poses followed by qs
images = []

# limitingCounter=3
# def getMean():
#blob = caffe.proto.caffe_pb2.BlobProto()
#data = open( meanFileLocation, 'rb' ).read()
# blob.ParseFromString(data)
#arr = np.array( caffe.io.blobproto_to_array(blob) )
# return arr[0]


# def ResizeCropImage(image):
# we need to keep in mind aspect ratio so the image does
# not look skewed or distorted -- therefore, we calculate
# the ratio of the new image to the old image
#   if image.shape[0]<image.shape[1]:
#      r = 256.0 / image.shape[0]
#     dim = ( 256,int(image.shape[1] * r))
# else:
#   r = 256.0 / image.shape[1]
#  dim = ( int(image.shape[0] * r),256)

# perform the actual resizing of the image and show it
# return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)[0:224, 0:224]
#cv2.imshow("resized", resized)
# cv2.waitKey(0)

meanImage = utilities.getMean()
# print meanImage.shape
# Test pretrained model
model = cnn_lstm.create_cnn_lstm(weightsfile)
sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd, loss='categorical_crossentropy')
#meantrasnformed = meanImage
#meantrasnformed[:,:,[0,1,2]]  = meanImage[:,:,[2,1,0]]
#meantrasnformed =  np.expand_dims(meantrasnformed, axis=0)
posxs = []
posqs = []
imgs = []
howmanyaccepted=0

counter = 0


with open(settings.testsetpath) as f:
    inputs = np.zeros([1, 3, 3, 224, 224])
    labels = np.zeros([3, 7])
    for line in f:
        fname, p0, p1, p2, p3, p4, p5, p6 = line.split()
        p0 = float(p0)
        p1 = float(p1)
        p2 = float(p2)
        p3 = float(p3)
        p4 = float(p4)
        p5 = float(p5)
        p6 = float(p6)
        posexyzwpqr = np.asarray((p0,p1,p2,p3,p4,p5,p6))
	img = utilities.ResizeCropImage(
            imread(directory + fname)).astype(np.float32)
	
        img = img.transpose((2, 0, 1))
        img[0, :, :] -= meanImage[0, :, :].mean()
        img[1, :, :] -= meanImage[1, :, :].mean()
        img[2, :, :] -= meanImage[2, :, :].mean()
        inputs[0, counter % settings.stepSize, :, :, :] = img
	labels[counter % settings.stepSize, :] =posexyzwpqr #np.asarray((p0,p1,p2,p3,p4,p5,p6))
	
        counter += 1
        if counter % 3 == 0:
            m1_2,a1_2 = getError(labels[0][:3],labels[0][3:7],labels[1][:3],labels[1][3:7])
            m2_3,a2_3 = getError(labels[1][:3],labels[1][3:7],labels[2][:3],labels[2][3:7])
            m1_3,a1_3 = getError(labels[0][:3],labels[0][3:7],labels[2][:3],labels[2][3:7])
            
            if m1_2 >settings.distanceThreshold or m2_3 >settings.distanceThreshold: 
		print m1_2,m2_3
                continue
            if a1_2 >settings.angleThreshold or a2_3 >settings.angleThreshold: 
                print a1_2,a2_3
		continue
            howmanyaccepted+=1
            out = model.predict(inputs)
	   # print out
	   # print out[0].shape #(1,3,3)
	    #print out
            posx = out[0][0][1]#.mean(0)#xyz
            posq = out[1][0][1]#.mean(0)#wpqr
            #print "actual:"
            actualx = labels[:,:3][1]#.mean(0)
            actualq = labels[:,3:7][1]#.mean(0)
            errx, theta = getError(posx,posq,actualx,actualq)
            posxs.append(errx)
            posqs.append(theta)
            print 'errx ', errx, ' m and ', 'errq ', theta, ' degrees'
            inputs = np.zeros([1, 3, 3, 224, 224])
	    labels = np.zeros([ 3, 7])
print 'median error', np.median(posxs), ' m and ', np.median(posqs), ' degrees'
print 'accepted test sequences: ',howmanyaccepted


    # poses.append((p0,p1,p2,p3,p4,p5,p6))
    # images.append(directory+fname)

    # imgs.append(img)
# print len(imgs)
# print 	np.asarray(imgs).shape
  # note: the model has three outputs
# out = model.predict(np.expand_dims(np.asarray(imgs),axis=0))  # note: the model has three outputs
# for i in range(len(out)):
#	for j in range(len(out[i])):
#		out[i][j]+=meanout[i][j]
# print np.argmax(out[2])
# print out
# print "predcited:"
