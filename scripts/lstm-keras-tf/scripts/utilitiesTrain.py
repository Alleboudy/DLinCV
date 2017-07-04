import numpy as np
#import caffe
import cv2
import random
import settings
from similarityMeasures import getError
directory = settings.directory
# "/usr/prakt/w065/posenet/OldHospital/"
data = settings.traindata  # 'KCorderedtrain.txt'
# print data
meanFile = settings.meanFile  # 'oldhospitaltrainmean.binaryproto'
batchSize = settings.batchSize
# resizes a given image so that the smallest dimension is 256 then crops
# 244X244 from the middle of it
# samplesCounter=0
fnames=[]

def ResizeCropImage(image):
    # we need to keep in mind aspect ratio so the image does
    # not look skewed or distorted -- therefore, we calculate
    # the ratio of the new image to the old image
    if image.shape[0] < image.shape[1]:
        r = 256.0 / image.shape[0]
        dim = (int(image.shape[1] * r), 256)
    else:
        r = 256.0 / image.shape[1]
        dim = (256, int(image.shape[0] * r))
        #dim is (cols,rows)

    # perform the actual resizing of the image and show it
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    centerWidth = image.shape[1] / 2
    centerHeight = image.shape[0] / 2
    return image[centerHeight - 112:centerHeight + 112, centerWidth - 112:centerWidth + 112]
    #cv2.imshow("resized", resized)
    # cv2.waitKey(0)

# extracts the mean image form a given mean file

def ResizeDifferentCrops(image):
    quarterHeight = int(image.shape[0]*0.75)
    quarterWidth = int(image.shape[1]*0.75)
    cornerImg1 =ResizeCropImage( image[:quarterHeight, :quarterWidth])
    cornerImg2 = ResizeCropImage(image[image.shape[0]-quarterHeight:, :quarterWidth])
    cornerImg3 = ResizeCropImage(image[image.shape[0]-quarterHeight:, image.shape[1]-quarterWidth:])
    cornerImg4 = ResizeCropImage(image[:quarterHeight, image.shape[1]-quarterWidth:])
    centerImg = ResizeCropImage(image[quarterHeight - int(quarterHeight/2):quarterHeight + int(quarterHeight/2), quarterWidth - int(quarterWidth/2):quarterWidth + int(quarterWidth/2)])
    wholeImg = ResizeCropImage(image)
    # cv2.imshow("lol1",cornerImg1)
    # cv2.imshow("lol2",cornerImg2)
    # cv2.imshow("lol3",cornerImg3)
    # cv2.imshow("lol4",cornerImg4)
    # cv2.imshow("lolcenter",centerImg)
    # cv2.waitKey()
    return (cornerImg1.astype(np.float32),cornerImg2.astype(np.float32),cornerImg3.astype(np.float32),cornerImg4.astype(np.float32),centerImg.astype(np.float32),wholeImg.astype(np.float32))

#def getMean():
    #blob = caffe.proto.caffe_pb2.BlobProto()
    #data = open( meanFileLocation, 'rb' ).read()
    # blob.ParseFromString(data)
    #arr = np.array( caffe.io.blobproto_to_array(blob) )
#    return np.load(meanFile)
    # return #arr[0]



def subtract_mean(images,saveMean=False):
    print "applying mean"
    mean = np.zeros((3, 224, 224))
    if saveMean:
	n=0
	for img in images:
   		mean[0] += img[0, :, :]
   		mean[1] += img[1, :, :]
    		mean[2] += img[2, :, :]
		n+=1
	mean/=n
	np.save(settings.meanFile,mean)
	print "mean saved in:"
#	print settings.meanFile
    else:
	mean=np.load(settings.meanFile)
	print "mean loaded from:"
    print settings.meanFile
    #old_mean_image = getMean()
   # print "old mean vs new mean!"
   # print old_mean_image==mean
    ready_images = []
    for img in images:
#	print img.shape
      if not settings.oldmean:
	#print "new mean"
        img-=mean
      else:
	#print "old mean"	
	img[0, :, :] -= mean[0,:,:].mean()
        img[1, :, :] -= mean[1,:,:].mean()
        img[2, :, :] -= mean[2,:,:].mean()
      ready_images.append(img)

    return ready_images




def get_data(dataset=data):
    images_batch1 = []
    images_batch2 = []
    images_batch3 = []
    images_batch4 = []
    images_batchCenter = []
    images_batchWhole = []
    po1 = []
    po2 = []
    # print 'in batch generator'
    # while(True):
   # while(True):
   # print 'lol1'
    # while(True):
    # print'lol2'
    print dataset
    with open(dataset) as f:
        print 'preparing data'
        #next(f)  # skip the 3 header lines
        #next(f)
        #next(f)
   # while(True):
        # print 'lol3'

        for line in f:
            if line.isspace():
                continue
	    #if settings.seqPrefix !='' and not line.startswith(settings.seqPrefix):
		#continue
	    print(line)
            fname, p0, p1, p2, p3, p4, p5, p6 = line.split()
            img1,img2,img3,img4,imgCenter,imgWhole = ResizeDifferentCrops(cv2.imread(
                directory + fname))#.astype(np.float32)
	    fnames.append(fname.split('/')[0])
            img1 = img1.transpose((2, 0, 1))
            img2 = img2.transpose((2, 0, 1))
            img3 = img3.transpose((2, 0, 1))
            img4 = img4.transpose((2, 0, 1))
            imgCenter = imgCenter.transpose((2, 0, 1))
            imgWhole = imgWhole.transpose((2, 0, 1))
            #img[0, :, :] -= meanImage[0, :, :].mean()
            #img[1, :, :] -= meanImage[1, :, :].mean()
            #img[2, :, :] -= meanImage[2, :, :].mean()
            #img[:, :, [0, 1, 2]] = img[:, :, [2, 1, 0]]
#                    img = np.expand_dims(img, axis=0)
            images_batch1.append(img1)
            images_batch2.append(img2)
            images_batch3.append(img3)
            images_batch4.append(img4)
            images_batchCenter.append(imgCenter)
            images_batchWhole.append(imgWhole)
            po1.append(np.array((np.float(p0), np.float(p1), np.float(p2))))
            po2.append(
                np.array((np.float(p3), np.float(p4), np.float(p5), np.float(p6))))

    ready_imgs1 = subtract_mean(np.asarray(images_batch1),True)
    ready_imgs2 = subtract_mean(np.asarray(images_batch2),True)
    ready_imgs3 = subtract_mean(np.asarray(images_batch3),True)
    ready_imgs4 = subtract_mean(np.asarray(images_batch4),True)
    ready_imgsCenter = subtract_mean(np.asarray(images_batchCenter),True)
    ready_imgsWhole = subtract_mean(np.asarray(images_batchWhole),True)
#       print po1.shape,p2.shape
    print "type is ########"
    print len(ready_imgs1)
    ready_imgs = ready_imgs1+ready_imgs2+ready_imgs3+ready_imgs4+ready_imgsCenter+ready_imgsWhole
    print len(ready_imgs)
    print type(po1)
    ready_imgs_lst = ready_imgs+[x for x in reversed(ready_imgs)]
    poses = po1+po1+po1+po1+po1+po1
    allposes=poses+[x for x in reversed(poses)]
    orts = po2+po2+po2+po2+po2+po2
    allorts = orts+[x for x in reversed(orts)]

    return (np.asarray(ready_imgs_lst), [np.asarray(allposes), np.asarray(allorts)])




def get_data_examples(source):
    #while True:
    indices = range(len(source[0]))
    #if settings.shuffle:
     #   random.shuffle(indices)
    for i in indices:
            image = source[0][i]
            image_left = source[0][max(0, i - 1)]
            image_right = source[0][min(i + 1, len(source[0]) - 1)]
            pose_x = source[1][0][i]
            pose_q = source[1][1][i]
            pose_x_left = source[1][0][max(0, i - 1)]
            pose_q_left = source[1][1][max(0, i - 1)]
            pose_x_right = source[1][0][min(i + 1, len(source[0]) - 1)]
            pose_q_right = source[1][1][min(i + 1, len(source[0]) - 1)]
       # print type(pose_x)
       # print pose_x
            # print pose_q
            # print pose_x_left
            m1_2, a1_2 = getError(pose_x, pose_q, pose_x_left, pose_q_left)
            m2_3, a2_3 = getError(pose_x, pose_q, pose_x_right, pose_q_right)
            m1_3, a1_3 = getError(pose_x_left, pose_q_left,
                                  pose_x_right, pose_q_right)
	    if fnames[i%len(fnames)]!=fnames[(i+1)%len(fnames)] or fnames[i%len(fnames)]!=fnames[(i-1)%len(fnames)]:
		print("skiped: "+ fnames[(i-1)%len(fnames)]+"_"+fnames[i%len(fnames)])+"_"+fnames[(i+1)%len(fnames)]
		continue
            if m1_2 > settings.distanceThreshold or m2_3 > settings.distanceThreshold:
                continue
            if a1_2 > settings.angleThreshold or a2_3 > settings.angleThreshold:
                continue
            #global samplesCounter
            # samplesCounter+=1
            # print samplesCounter
            yield np.asarray([image_left, image, image_right]), np.asarray([pose_x, pose_x_left, pose_x_right]), np.asarray([pose_q, pose_q_left, pose_q_right])





def gen_data_batch(source):
    data_gen = gen_data(source)
    while True:
        image_batch = []
        pose_x_batch = []
        pose_q_batch = []
        for _ in range(batchSize):
            image, pose_x, pose_q = next(data_gen)
            image_batch.append(image)
            pose_x_batch.append(pose_x)
            pose_q_batch.append(pose_q)
        yield np.asarray(image_batch), [np.asarray(pose_x_batch), np.asarray(pose_q_batch)]


