import cv2 as cv
import numpy as np
from collections import deque

im = cv.imread('abdomen.png')
im = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
w = im.shape[1]
h = im.shape[0]

mask = np.zeros([h,w,2], np.uint8)

def segmentation(im, mask, x0,y0,diff=9):
    max_x =im.shape[0]
    max_y = im.shape[1]
    loops = max_x*max_y
    counter =0
    q = deque()
    q.appendleft((x0,y0))
    while not len(q) == 0:
        counter+=1
        if(counter%(int(loops/1000))==0):
            print('c={} {}%'.format(counter,(counter/loops)*100))
        xc,yc =q.pop()
        if mask[xc][yc][1]==2:
            continue
        mask[xc][yc]=2
        mask[xc][yc][0]=255
        ref_val = int(im[xc][yc])
        for x in [xc-1,xc,xc+1]:
            if x< 0 or x >= max_x:
                continue
            for y in [yc-1,yc,yc+1]:
                if y < 0 or y >= max_y:
                    continue
                tmp_val=int(im[x][y])
                # print ('ref_val={} im[x][y]={} diff={}'.format(ref_val,tmp_val,abs(tmp_val-ref_val)))
                if mask[x][y][1] == 0 and abs(ref_val-tmp_val) < diff:
                    mask[x][y][1] = 1
                    q.appendleft((x,y))


    im_out = np.reshape(mask[:,:,:-1],im.shape)
    cv.imshow('seg0',im_out)
    # mask[:,:,:]=  np.zeros([h,w,2], np.uint8)
    return im_out


def mouse_callback(event, x, y, flags, params):
    if event ==1:
        print([x,y])
        print(im[y, x])
        out_img = segmentation(im,mask,y,x)
        kernel = np.ones((5,5),np.uint8)
        # dilation = cv.dilate(out_img,kernel,iterations= 1)
        # cv.imshow('dilation',dilation)
        closed = cv.morphologyEx(out_img, cv.MORPH_CLOSE, kernel)
        cv.imshow('closed',closed)
        edges = cv.Canny(closed,0.2,0.4)
        cv.imshow('edges',edges)


cv.imshow('image',im)
cv.setMouseCallback('image', mouse_callback)
cv.waitKey()
cv.destroyAllWindows()
