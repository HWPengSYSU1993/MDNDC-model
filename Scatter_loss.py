import tensorflow as tf

def SLloss(embeddings,class_num,sample_class,embedding_size,Deta=1.5):
    """Calculate the SL loss

    Args:
      embedding_size: the embeddings dimentions.
      sample_class: the number of samples each subject.
      class_num: the number of people each batch.
      embeddings: the extracting features from the network. 
      Deta: the margin value

    Returns:
      the SL loss as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    labelsIdx = tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean = tf.segment_mean(embeddings, labelsIdx, name='class_mean')
        all_class_center = tf.segment_mean(embeddings, labelzero, name='class_mean')
        val_Multiply_class=tf.constant(1/(class_num*class_num-class_num)) #(class_num*class_num+class_num)/2  ??
        val_Multiply_sample = tf.constant(1/(sample_class*class_num))
        print('all_class_center', all_class_center)
        print('class_mean',class_mean)
        sampleNum=0
        for classIdx in range(class_num):
            class_mean_single=tf.slice(class_mean,[classIdx,0],[1,embedding_size])
            for classIdx2 in range(classIdx+1,class_num):
                class_mean_single_other = tf.slice(class_mean, [classIdx2, 0], [1, embedding_size])
                class_mean_single_subtract = tf.subtract(class_mean_single, class_mean_single_other)
                class_mean_single_subtract_square = tf.square(class_mean_single_subtract)
                neg_dist = tf.reduce_sum(class_mean_single_subtract_square)
                Sb_loss = tf.add(tf.subtract(0.0, neg_dist), Deta)
                Sb_loss = tf.maximum(Sb_loss, 0.0)
                class_mean_single_subtract_square = tf.multiply(Sb_loss, val_Multiply_class)
                if classIdx==0 and classIdx2==1:
                    Sb = class_mean_single_subtract_square
                else:
                    Sb = tf.add(Sb,class_mean_single_subtract_square)
                print('classIdx2',classIdx,classIdx2)
            for sampleIdx in range(sample_class):
                sample_embeddings = tf.slice(embeddings, [sampleNum, 0], [1, embedding_size])
                class_embeddings_subtract = tf.subtract(sample_embeddings, class_mean_single)
                class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                pos_dist = tf.reduce_sum(class_embeddings_subtract_square)
                class_embeddings_subtract_square = tf.multiply(pos_dist, val_Multiply_sample)
                if sampleNum==0:
                    Sw = class_embeddings_subtract_square
                    print('Sw = Sw_Tmp',sampleNum)
                else:
                    Sw = tf.add(Sw, class_embeddings_subtract_square)
                    print('Sw = tf.add(Sw, Sw_Tmp)',sampleNum)
                sampleNum += 1
            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)


        print('Sw',Sw)
        print('Sb',Sb)
        
        loss = tf.add(Sw, Sb)
        print('loss', loss)

    return loss



def Contrastive_loss(embeddings,class_num,sample_class,embedding_size,Deta=0.5):# 20180818 Deta (20190311: MDNDC paper SL loss)
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    # labelsIdx = tf.constant(labelsIdx)

    sample_num=sample_class*class_num
    pos_num=0
    neg_num=0
    with tf.variable_scope('RQ_loss'):
        for sampleIdx in range(sample_num):
            sample_embeddings = tf.slice(embeddings, [sampleIdx, 0], [1, embedding_size])
            class1=labelsIdx[sampleIdx]
            for sampleIdx2 in range(sampleIdx+1,sample_num):
                sample_embeddings2=tf.slice(embeddings, [sampleIdx2, 0], [1, embedding_size])
                class2 = labelsIdx[sampleIdx2]
                #intra-class
                if class1==class2:
                    pos_num+=1

                    class_embeddings_subtract = tf.subtract(sample_embeddings, sample_embeddings2)
                    class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                    pos_dist = tf.reduce_sum(class_embeddings_subtract_square)
                    if sampleIdx==0:
                        Sw=pos_dist
                    else:
                        Sw += pos_dist
                    print('intra-class',sampleIdx,sampleIdx2)
                # inter-class
                else:
                    neg_num+=1
                    class_embeddings_subtract = tf.subtract(sample_embeddings, sample_embeddings2)
                    class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                    neg_dist = tf.reduce_sum(class_embeddings_subtract_square)
                    neg_dist_ = tf.subtract(Deta, neg_dist)
                    neg_dist_ = tf.maximum(neg_dist_, 0.0)

                    if sampleIdx==0:
                        Sb=neg_dist_
                    else:
                        Sb += neg_dist_
                    print('inter-class', sampleIdx, sampleIdx2)
        Sw = tf.multiply(Sw, 1/pos_num)
        Sb = tf.multiply(Sb, 1 / neg_num)

        print('Sw',Sw)
        print('Sb',Sb)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        # loss = tf.divide(tf.reduce_sum(Sw), tf.reduce_sum(Sb))
        # pos_dist=tf.reduce_sum(Sw)
        # neg_dist=tf.reduce_sum(Sb)
        # loss = tf.subtract(pos_dist, neg_dist)
        # alpha=0.2
        # basic_loss = tf.add(tf.subtract(pos_dist,neg_dist), alpha)
        # loss = tf.maximum(basic_loss, 0.0)

        loss = tf.add(Sw, Sb)
        print('loss', loss)

    return loss

















def RQlossDeta_alpha(embeddings,class_num,sample_class,embedding_size):# loss = class subtract class
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    labelsIdx = tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean = tf.segment_mean(embeddings, labelsIdx, name='class_mean')
        all_class_center = tf.segment_mean(embeddings, labelzero, name='class_mean')
        val_Multiply_class=tf.constant(1/(class_num*class_num-class_num))
        val_Multiply_sample = tf.constant(1/(sample_class*class_num))
        print('all_class_center', all_class_center)
        print('class_mean',class_mean)
        sampleNum=0
        Deta=4

        for classIdx in range(class_num):

            class_mean_single=tf.slice(class_mean,[classIdx,0],[1,embedding_size])

            for classIdx2 in range(classIdx+1,class_num):
                class_mean_single_other = tf.slice(class_mean, [classIdx2, 0], [1, embedding_size])
                class_mean_single_subtract = tf.subtract(class_mean_single, class_mean_single_other)
                class_mean_single_subtract_square = tf.square(class_mean_single_subtract)

                neg_dist = tf.reduce_sum(class_mean_single_subtract_square)
                Sb_loss = tf.add(tf.subtract(0.0, neg_dist), Deta)
                Sb_loss = tf.maximum(Sb_loss, 0.0)


                class_mean_single_subtract_square = tf.multiply(Sb_loss, val_Multiply_class)
                if classIdx==0 and classIdx2==1:
                    Sb = class_mean_single_subtract_square
                else:
                    Sb = tf.add(Sb,class_mean_single_subtract_square)
                print('classIdx2',classIdx,classIdx2)

            alpha = 0.05

            for sampleIdx in range(sample_class):


                sample_embeddings = tf.slice(embeddings, [sampleNum, 0], [1, embedding_size])
                class_embeddings_subtract = tf.subtract(sample_embeddings, class_mean_single)
                class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                pos_dist = tf.reduce_sum(class_embeddings_subtract_square)

                Sw_loss = tf.subtract(pos_dist, alpha)
                Sw_loss = tf.maximum(Sw_loss, 0.0)

                class_embeddings_subtract_square = tf.multiply(Sw_loss, val_Multiply_sample)

                if sampleNum==0:
                    Sw = class_embeddings_subtract_square
                    print('Sw = Sw_Tmp',sampleNum)
                else:
                    Sw = tf.add(Sw, class_embeddings_subtract_square)
                    print('Sw = tf.add(Sw, Sw_Tmp)',sampleNum)

                sampleNum += 1

            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)


        print('Sw',Sw)
        print('Sb',Sb)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        # loss = tf.divide(tf.reduce_sum(Sw), tf.reduce_sum(Sb))
        # pos_dist=tf.reduce_sum(Sw)
        # neg_dist=tf.reduce_sum(Sb)
        # loss = tf.subtract(pos_dist, neg_dist)
        # alpha=0.2
        # basic_loss = tf.add(tf.subtract(pos_dist,neg_dist), alpha)
        # loss = tf.maximum(basic_loss, 0.0)

        loss = tf.add(Sw, Sb)
        print('loss', loss)

    return loss



def RQloss_nice(embeddings,class_num,sample_class,embedding_size):# loss = class subtract class
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    labelsIdx = tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean = tf.segment_mean(embeddings, labelsIdx, name='class_mean')
        all_class_center = tf.segment_mean(embeddings, labelzero, name='class_mean')
        val_Multiply_class=tf.constant(1/(class_num*class_num-class_num))
        val_Multiply_sample = tf.constant(1/(sample_class*class_num))
        print('all_class_center', all_class_center)
        print('class_mean',class_mean)
        sampleNum=0
        for classIdx in range(class_num):

            class_mean_single=tf.slice(class_mean,[classIdx,0],[1,embedding_size])

            for classIdx2 in range(classIdx+1,class_num):
                class_mean_single_other = tf.slice(class_mean, [classIdx2, 0], [1, embedding_size])
                class_mean_single_subtract = tf.subtract(class_mean_single, class_mean_single_other)
                class_mean_single_subtract_square = tf.square(class_mean_single_subtract)
                class_mean_single_subtract_square = tf.multiply(class_mean_single_subtract_square, val_Multiply_class)
                if classIdx==0 and classIdx2==1:
                    Sb = class_mean_single_subtract_square
                else:
                    Sb = tf.add(Sb,class_mean_single_subtract_square)
                print('classIdx2',classIdx,classIdx2)
            for sampleIdx in range(sample_class):


                sample_embeddings = tf.slice(embeddings, [sampleNum, 0], [1, embedding_size])
                class_embeddings_subtract = tf.subtract(sample_embeddings, class_mean_single)
                class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                class_embeddings_subtract_square = tf.multiply(class_embeddings_subtract_square, val_Multiply_sample)

                if sampleNum==0:
                    Sw = class_embeddings_subtract_square
                    print('Sw = Sw_Tmp',sampleNum)
                else:
                    Sw = tf.add(Sw, class_embeddings_subtract_square)
                    print('Sw = tf.add(Sw, Sw_Tmp)',sampleNum)

                sampleNum += 1

            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)


        print('Sw',Sw)
        print('Sb',Sb)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        # loss = tf.divide(tf.reduce_sum(Sw), tf.reduce_sum(Sb))
        # pos_dist=tf.reduce_sum(Sw)
        # neg_dist=tf.reduce_sum(Sb)
        # loss = tf.subtract(pos_dist, neg_dist)
        # alpha=0.2
        # basic_loss = tf.add(tf.subtract(pos_dist,neg_dist), alpha)
        # loss = tf.maximum(basic_loss, 0.0)


        Sw_sum=tf.reduce_sum(Sw)
        Sb_sum = tf.reduce_sum(Sb)
        print('Sw_sum', Sw_sum)
        print('Sb_sum', Sb_sum)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        loss = tf.divide(Sw_sum, Sb_sum)
        print('loss', loss)

    return loss



def RQlossADD(embeddings,class_num,sample_class,embedding_size):# loss = tf.div(tf.trace(Sw), tf.trace(Sb))
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    labelsIdx = tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean = tf.segment_mean(embeddings, labelsIdx, name='class_mean')
        all_class_center = tf.segment_mean(embeddings, labelzero, name='class_mean')
        val_Multiply_class=tf.constant(1/class_num)
        val_Multiply_sample = tf.constant(1/(sample_class*class_num))
        print('all_class_center', all_class_center)
        print('class_mean',class_mean)
        sampleNum=0
        for classIdx in range(class_num):

            class_mean_single=tf.slice(class_mean,[classIdx,0],[1,embedding_size])
            class_mean_single_subtract = tf.subtract(class_mean_single, all_class_center)
            class_mean_single_subtract_square=tf.square(class_mean_single_subtract)
            class_mean_single_subtract_square=tf.multiply(class_mean_single_subtract_square,val_Multiply_class)
            if classIdx==0:
                Sb = class_mean_single_subtract_square
            else:
                Sb = tf.add(Sb,class_mean_single_subtract_square)
            for sampleIdx in range(sample_class):


                sample_embeddings = tf.slice(embeddings, [sampleNum, 0], [1, embedding_size])
                class_embeddings_subtract = tf.subtract(sample_embeddings, class_mean_single)
                class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                class_mean_single_subtract_square = tf.multiply(class_embeddings_subtract_square, val_Multiply_sample)

                if sampleNum==0:
                    Sw = class_mean_single_subtract_square
                    print('Sw = Sw_Tmp',sampleNum)
                else:
                    Sw = tf.add(Sw, class_mean_single_subtract_square)
                    print('Sw = tf.add(Sw, Sw_Tmp)',sampleNum)

                sampleNum += 1

            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)


        print('Sw',Sw)
        print('Sb',Sb)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        # loss = tf.divide(tf.reduce_sum(Sw), tf.reduce_sum(Sb))
        pos_dist=tf.reduce_sum(Sw)
        neg_dist=tf.reduce_sum(Sb)
        loss = tf.subtract(pos_dist, neg_dist)
        # alpha=0.2
        # basic_loss = tf.add(tf.subtract(pos_dist,neg_dist), alpha)
        # loss = tf.maximum(basic_loss, 0.0)
        print('loss', loss)

    return loss


def RQloss_square(embeddings, class_num, sample_class, embedding_size):  # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    labelsIdx = tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean = tf.segment_mean(embeddings, labelsIdx, name='class_mean')
        all_class_center = tf.segment_mean(embeddings, labelzero, name='class_mean')
        # all_class_center = tf.reduce_mean(embeddings, 0)
        val_Multiply_class = tf.constant(1 / class_num)
        val_Multiply_sample = tf.constant(1 / (sample_class * class_num))
        print('all_class_center', all_class_center)
        print('class_mean', class_mean)
        sampleNum = 0
        for classIdx in range(class_num):

            class_mean_single = tf.slice(class_mean, [classIdx, 0], [1, embedding_size])
            class_mean_single_subtract = tf.subtract(class_mean_single, all_class_center)
            class_mean_single_subtract_square = tf.square(class_mean_single_subtract)
            class_mean_single_subtract_square = tf.multiply(class_mean_single_subtract_square, val_Multiply_class)
            if classIdx == 0:
                Sb = class_mean_single_subtract_square
            else:
                Sb = tf.add(Sb, class_mean_single_subtract_square)
            for sampleIdx in range(sample_class):

                sample_embeddings = tf.slice(embeddings, [sampleNum, 0], [1, embedding_size])
                sample_embeddings_subtract = tf.subtract(sample_embeddings, class_mean_single)
                sample_embeddings_subtract_square = tf.square(sample_embeddings_subtract)
                sample_embeddings_subtract_square = tf.multiply(sample_embeddings_subtract_square, val_Multiply_sample)

                if sampleNum == 0:
                    Sw = sample_embeddings_subtract_square
                    print('Sw = Sw_Tmp', sampleNum)
                else:
                    Sw = tf.add(Sw, sample_embeddings_subtract_square)
                    print('Sw = tf.add(Sw, Sw_Tmp)', sampleNum)

                sampleNum += 1
                print('sample_embeddings', sample_embeddings)
                print('sample_embeddings_subtract', sample_embeddings_subtract)
                print('sample_embeddings_subtract_square', sample_embeddings_subtract_square)

            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)
            print('class_mean_single_subtract_square', class_mean_single_subtract_square)
        print('Sw',Sw)
        print('Sb',Sb)
        Sw_sum=tf.reduce_sum(Sw)
        Sb_sum = tf.reduce_sum(Sb)
        print('Sw_sum', Sw_sum)
        print('Sb_sum', Sb_sum)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        loss = tf.divide(Sw_sum, Sb_sum)
    return loss


def RQloss_good(embeddings,class_num,sample_class,embedding_size):# loss = tf.div(tf.trace(Sw), tf.trace(Sb))
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []
    labelzero=[]
    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
            labelzero.append(0)
    print('labelsIdx', labelsIdx)
    labelsIdx = tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean=tf.segment_mean(embeddings,labelsIdx,name='class_mean')
        all_class_center = tf.segment_mean(embeddings, labelzero, name='class_mean')
        # all_class_center=tf.reduce_mean(embeddings,0)
        val_Multiply_class=tf.constant(1/class_num)
        val_Multiply_sample = tf.constant(1/(sample_class*class_num))
        print('all_class_center', all_class_center)
        print('class_mean',class_mean)
        sampleNum=0
        for classIdx in range(class_num):

            class_mean_single=tf.slice(class_mean,[classIdx,0],[1,embedding_size])


            class_mean_single_subtract=tf.subtract(class_mean_single, all_class_center)
            Sb_Tmp=tf.multiply(tf.matmul(tf.transpose(class_mean_single_subtract, perm=[1, 0]),class_mean_single_subtract),val_Multiply_class)
            print('Sb_Tmp', Sb_Tmp)
            if classIdx==0:
                Sb = Sb_Tmp
            else:
                Sb = tf.add(Sb,Sb_Tmp)

            class_embeddings = tf.slice(embeddings, [sampleNum, 0], [sample_class, embedding_size])
            class_mean_single_tile=tf.tile(class_mean_single,[sample_class,1])
            class_embeddings_subtract=tf.subtract(class_embeddings,class_mean_single_tile)
            Sw_Tmp=tf.multiply(tf.matmul(tf.transpose(class_embeddings_subtract, perm=[1, 0]), class_embeddings_subtract),val_Multiply_sample)
            print('Sw_Tmp', Sw_Tmp)
            if classIdx==0:
                Sw = Sw_Tmp
                print('Sw = Sw_Tmp')
            else:
                Sw = tf.add(Sw, Sw_Tmp)
                print('Sw = tf.add(Sw, Sw_Tmp)')


            print('sampleNum', sampleNum)
            sampleNum = sample_class + sampleNum

            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)

            print('class_embeddings', class_embeddings)
            print('class_mean_single_tile', class_mean_single_tile)
            print('class_embeddings_subtract', class_embeddings_subtract)

        print('Sw',Sw)
        print('Sb',Sb)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        loss = tf.divide(tf.trace(Sw), tf.trace(Sb))
        print('loss', loss)

    return loss

def RQlossoLD(embeddings,class_num,sample_class,embedding_size):# loss = tf.div(tf.trace(Sw), tf.trace(Sb))
    """Calculate the triplet loss according to the FaceNet paper

    Args:
      anchor: the embeddings for the anchor images.
      positive: the embeddings for the positive images.
      negative: the embeddings for the negative images.

    Returns:
      the triplet loss according to the FaceNet paper as a float tensor.
    """
    labelsIdx = []

    for idx in range(class_num):
        for i in range(sample_class):
            labelsIdx.append(idx)
    print('labelsIdx',labelsIdx)
    labelsIdx=tf.constant(labelsIdx)

    with tf.variable_scope('RQ_loss'):
        class_mean=tf.segment_mean(embeddings,labelsIdx,name='class_mean')
        all_class_center=tf.reduce_mean(embeddings,0)
        val_Multiply_class=tf.constant(1/class_num)
        val_Multiply_sample = tf.constant(1/(sample_class*class_num))
        print('all_class_center', all_class_center)
        print('class_mean',class_mean)
        sampleNum=0
        for classIdx in range(class_num):

            class_mean_single=tf.slice(class_mean,[classIdx,0],[1,embedding_size])
            class_mean_single_subtract = tf.subtract(class_mean_single, all_class_center)
            class_mean_single_subtract_square=tf.square(class_mean_single_subtract)
            class_mean_single_subtract_square=tf.multiply(class_mean_single_subtract_square,val_Multiply_class)
            if classIdx==0:
                Sb = class_mean_single_subtract_square
            else:
                Sb = tf.add(Sb,class_mean_single_subtract_square)
            for sampleIdx in range(sample_class):


                sample_embeddings = tf.slice(embeddings, [sampleNum, 0], [1, embedding_size])
                class_embeddings_subtract = tf.subtract(sample_embeddings, class_mean_single)
                class_embeddings_subtract_square = tf.square(class_embeddings_subtract)
                class_mean_single_subtract_square = tf.multiply(class_embeddings_subtract_square, val_Multiply_sample)

                if sampleNum==0:
                    Sw = class_mean_single_subtract_square
                    print('Sw = Sw_Tmp',sampleNum)
                else:
                    Sw = tf.add(Sw, class_mean_single_subtract_square)
                    print('Sw = tf.add(Sw, Sw_Tmp)',sampleNum)

                sampleNum += 1
                print('sample_embeddings', sample_embeddings)
                print('class_embeddings_subtract', class_embeddings_subtract)
                print('class_embeddings_subtract_square', class_embeddings_subtract_square)
                print('class_mean_single_subtract_square', class_mean_single_subtract_square)

            print('class_mean_single', class_mean_single)
            print('class_mean_single_subtract', class_mean_single_subtract)
            print('class_mean_single_subtract_square', class_mean_single_subtract_square)

        print('Sw',Sw)
        print('Sb',Sb)
        Sw_sum=tf.reduce_sum(Sw)
        Sb_sum = tf.reduce_sum(Sb)
        print('Sw_sum', Sw_sum)
        print('Sb_sum', Sb_sum)
        # loss = tf.div(tf.trace(Sw), tf.trace(Sb))
        loss = tf.divide(Sw_sum, Sb_sum)

        print('loss', loss)

    return loss


def decov_loss(xs):
    """Decov loss as described in https://arxiv.org/pdf/1511.06068.pdf
    'Reducing Overfitting In Deep Networks by Decorrelating Representation'
    """
    x = tf.reshape(xs, [int(xs.get_shape()[0]), -1])
    m = tf.reduce_mean(x, 0, True)
    z = tf.expand_dims(x-m, 2)
    corr = tf.reduce_mean(tf.matmul(z, tf.transpose(z, perm=[0,2,1])), 0)
    corr_frob_sqr = tf.reduce_sum(tf.square(corr))
    corr_diag_sqr = tf.reduce_sum(tf.square(tf.diag_part(corr)))
    loss = 0.5*(corr_frob_sqr - corr_diag_sqr)
    return loss 
  
def center_loss(features, label, alfa, nrof_classes):
    """Center loss based on the paper "A Discriminative Feature Learning Approach for Deep Face Recognition"
       (http://ydwen.github.io/papers/WenECCV16.pdf)
    """
    nrof_features = features.get_shape()[1]
    centers = tf.get_variable('centers', [nrof_classes, nrof_features], dtype=tf.float32,
        initializer=tf.constant_initializer(0), trainable=False)
    label = tf.reshape(label, [-1])
    centers_batch = tf.gather(centers, label)
    diff = (1 - alfa) * (centers_batch - features)
    centers = tf.scatter_sub(centers, label, diff)
    loss = tf.reduce_mean(tf.square(features - centers_batch))
    return loss, centers

def get_image_paths_and_labels(dataset):
    image_paths_flat = []
    labels_flat = []
    for i in range(len(dataset)):
        image_paths_flat += dataset[i].image_paths
        labels_flat += [i] * len(dataset[i].image_paths)
    return image_paths_flat, labels_flat

def shuffle_examples(image_paths, labels):
    shuffle_list = list(zip(image_paths, labels))
    random.shuffle(shuffle_list)
    image_paths_shuff, labels_shuff = zip(*shuffle_list)
    return image_paths_shuff, labels_shuff

def read_images_from_disk(input_queue):
    """Consumes a single filename and label as a ' '-delimited string.
    Args:
      filename_and_label_tensor: A scalar string tensor.
    Returns:
      Two tensors: the decoded image, and the string label.
    """
    label = input_queue[1]
    file_contents = tf.read_file(input_queue[0])
    example = tf.image.decode_image(file_contents, channels=3)
    return example, label
  
def random_rotate_image(image):
    angle = np.random.uniform(low=-10.0, high=10.0)
    return misc.imrotate(image, angle, 'bicubic')
  
def read_and_augment_data(image_list, label_list, image_size, batch_size, max_nrof_epochs, 
        random_crop, random_flip, random_rotate, nrof_preprocess_threads, shuffle=True):
    
    images = ops.convert_to_tensor(image_list, dtype=tf.string)
    labels = ops.convert_to_tensor(label_list, dtype=tf.int32)
    
    # Makes an input queue
    input_queue = tf.train.slice_input_producer([images, labels],
        num_epochs=max_nrof_epochs, shuffle=shuffle)

    images_and_labels = []
    for _ in range(nrof_preprocess_threads):
        image, label = read_images_from_disk(input_queue)
        if random_rotate:
            image = tf.py_func(random_rotate_image, [image], tf.uint8)
        if random_crop:
            image = tf.random_crop(image, [image_size, image_size, 3])
        else:
            image = tf.image.resize_image_with_crop_or_pad(image, image_size, image_size)
        if random_flip:
            image = tf.image.random_flip_left_right(image)
        #pylint: disable=no-member
        image.set_shape((image_size, image_size, 3))
        image = tf.image.per_image_standardization(image)
        images_and_labels.append([image, label])

    image_batch, label_batch = tf.train.batch_join(
        images_and_labels, batch_size=batch_size,
        capacity=4 * nrof_preprocess_threads * batch_size,
        allow_smaller_final_batch=True)
  
    return image_batch, label_batch


# 1: Random rotate 2: Random crop  4: Random flip  8:  Fixed image standardization  16: Flip
RANDOM_ROTATE = 1
RANDOM_CROP = 2
RANDOM_FLIP = 4
FIXED_STANDARDIZATION = 8
FLIP = 16

def create_input_pipeline(input_queue, image_size, nrof_preprocess_threads, batch_size_placeholder):
    images_and_labels_list = []
    for _ in range(nrof_preprocess_threads):
        filenames, label, control = input_queue.dequeue()
        images = []
        for filename in tf.unstack(filenames):
            file_contents = tf.read_file(filename)
            image = tf.image.decode_image(file_contents, 3)
            image = tf.cond(get_control_flag(control[0], RANDOM_ROTATE),
                            lambda: tf.py_func(random_rotate_image, [image], tf.uint8),
                            lambda: tf.identity(image))
            image = tf.cond(get_control_flag(control[0], RANDOM_CROP),
                            lambda: tf.random_crop(image, image_size + (3,)),
                            lambda: tf.image.resize_image_with_crop_or_pad(image, image_size[0], image_size[1]))
            image = tf.cond(get_control_flag(control[0], RANDOM_FLIP),
                            lambda: tf.image.random_flip_left_right(image),
                            lambda: tf.identity(image))
            image = tf.cond(get_control_flag(control[0], FIXED_STANDARDIZATION),
                            lambda: (tf.cast(image, tf.float32) - 127.5) / 128.0,
                            lambda: tf.image.per_image_standardization(image))
            image = tf.cond(get_control_flag(control[0], FLIP),
                            lambda: tf.image.flip_left_right(image),
                            lambda: tf.identity(image))
            # pylint: disable=no-member
            image.set_shape(image_size + (3,))
            images.append(image)
        images_and_labels_list.append([images, label])

    image_batch, label_batch = tf.train.batch_join(
        images_and_labels_list, batch_size=batch_size_placeholder,
        shapes=[image_size + (3,), ()], enqueue_many=True,
        capacity=4 * nrof_preprocess_threads * 100,
        allow_smaller_final_batch=True)

    return image_batch, label_batch


def get_control_flag(control, field):
    return tf.equal(tf.mod(tf.floor_div(control, field), 2), 1)

def _add_loss_summaries(total_loss):
    """Add summaries for losses.
  
    Generates moving average for all losses and associated summaries for
    visualizing the performance of the network.
  
    Args:
      total_loss: Total loss from loss().
    Returns:
      loss_averages_op: op for generating moving averages of losses.
    """
    # Compute the moving average of all individual losses and the total loss.
    loss_averages = tf.train.ExponentialMovingAverage(0.9, name='avg')
    losses = tf.get_collection('losses')
    tmp_loss = losses + [total_loss]
    loss_averages_op = loss_averages.apply(losses + [total_loss])
  
    # Attach a scalar summmary to all individual losses and the total loss; do the
    # same for the averaged version of the losses.
    for l in losses + [total_loss]:
        # Name each loss as '(raw)' and name the moving average version of the loss
        # as the original loss name.
        tf.summary.scalar(l.op.name +' (raw)', l)
        tf.summary.scalar(l.op.name, loss_averages.average(l))
  
    return loss_averages_op

def train(total_loss, global_step, optimizer, learning_rate, moving_average_decay, update_gradient_vars, log_histograms=True):
    # Generate moving averages of all losses and associated summaries.
    loss_averages_op = _add_loss_summaries(total_loss)

    # Compute gradients.
    with tf.control_dependencies([loss_averages_op]):
        if optimizer=='ADAGRAD':
            opt = tf.train.AdagradOptimizer(learning_rate)
        elif optimizer=='ADADELTA':
            opt = tf.train.AdadeltaOptimizer(learning_rate, rho=0.9, epsilon=1e-6)
        elif optimizer=='ADAM':
            opt = tf.train.AdamOptimizer(learning_rate, beta1=0.9, beta2=0.999, epsilon=0.1)
        elif optimizer=='RMSPROP':
            opt = tf.train.RMSPropOptimizer(learning_rate, decay=0.9, momentum=0.9, epsilon=1.0)
        elif optimizer=='MOM':
            opt = tf.train.MomentumOptimizer(learning_rate, 0.9, use_nesterov=True)
        else:
            raise ValueError('Invalid optimization algorithm')
    
        grads = opt.compute_gradients(total_loss, update_gradient_vars)

        
    # Apply gradients.
    apply_gradient_op = opt.apply_gradients(grads, global_step=global_step)
  
    # Add histograms for trainable variables.
    if log_histograms:
        for var in tf.trainable_variables():
            tf.summary.histogram(var.op.name, var)
   
    # Add histograms for gradients.
    if log_histograms:
        for grad, var in grads:
            if grad is not None:
                tf.summary.histogram(var.op.name + '/gradients', grad)
  
    # Track the moving averages of all trainable variables.
    variable_averages = tf.train.ExponentialMovingAverage(
        moving_average_decay, global_step)
    variables_averages_op = variable_averages.apply(tf.trainable_variables())
  
    with tf.control_dependencies([apply_gradient_op, variables_averages_op]):
        train_op = tf.no_op(name='train')
  
    return train_op

#TODO select variable to train
def train_partVar(total_loss, global_step, optimizer, learning_rate, moving_average_decay, update_gradient_vars,
          log_histograms=True):
    # Generate moving averages of all losses and associated summaries.
    loss_averages_op = _add_loss_summaries(total_loss)

    # Compute gradients.
    with tf.control_dependencies([loss_averages_op]):
        if optimizer == 'ADAGRAD':
            opt = tf.train.AdagradOptimizer(learning_rate)
        elif optimizer == 'ADADELTA':
            opt = tf.train.AdadeltaOptimizer(learning_rate, rho=0.9, epsilon=1e-6)
        elif optimizer == 'ADAM':
            opt = tf.train.AdamOptimizer(learning_rate, beta1=0.9, beta2=0.999, epsilon=0.1)
        elif optimizer == 'RMSPROP':
            opt = tf.train.RMSPropOptimizer(learning_rate, decay=0.9, momentum=0.9, epsilon=1.0)
        elif optimizer == 'MOM':
            opt = tf.train.MomentumOptimizer(learning_rate, 0.9, use_nesterov=True)
        else:
            raise ValueError('Invalid optimization algorithm')

        grads = opt.compute_gradients(total_loss, update_gradient_vars)
        # grads = tf.Print(grads, [grads], message='The grad:')
    # Apply gradients.
    apply_gradient_op = opt.apply_gradients(grads, global_step=global_step)

    # Add histograms for trainable variables.
    if log_histograms:
        for var in tf.trainable_variables():
            tf.summary.histogram(var.op.name, var)

    # Add histograms for gradients.
    if log_histograms:
        for grad, var in grads:
            if grad is not None:
                tf.summary.histogram(var.op.name + '/gradients', grad)

    # Track the moving averages of all trainable variables.
    variable_averages = tf.train.ExponentialMovingAverage(
        moving_average_decay, global_step)
    variables_averages_op = variable_averages.apply(update_gradient_vars)

    with tf.control_dependencies([apply_gradient_op, variables_averages_op]):
        train_op = tf.no_op(name='train')

    return train_op

def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1/std_adj)
    return y  

def crop(image, random_crop, image_size):
    if image.shape[1]>image_size:
        sz1 = int(image.shape[1]//2)
        sz2 = int(image_size//2)
        if random_crop:
            diff = sz1-sz2
            (h, v) = (np.random.randint(-diff, diff+1), np.random.randint(-diff, diff+1))
        else:
            (h, v) = (0,0)
        image = image[(sz1-sz2+v):(sz1+sz2+v),(sz1-sz2+h):(sz1+sz2+h),:]
    return image
  
def flip(image, random_flip):
    if random_flip and np.random.choice([True, False]):
        image = np.fliplr(image)
    return image

def to_rgb(img):
    w, h = img.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img
    return ret
  
def load_data(image_paths, do_random_crop, do_random_flip, image_size, do_prewhiten=True):
    nrof_samples = len(image_paths)
    images = np.zeros((nrof_samples, image_size, image_size, 3))
    for i in range(nrof_samples):
        img = misc.imread(image_paths[i])
        if img.ndim == 2:
            img = to_rgb(img)
        if do_prewhiten:
            img = prewhiten(img)
        img = crop(img, do_random_crop, image_size)
        img = flip(img, do_random_flip)
        images[i,:,:,:] = img
    return images

def get_label_batch(label_data, batch_size, batch_index):
    nrof_examples = np.size(label_data, 0)
    j = batch_index*batch_size % nrof_examples
    if j+batch_size<=nrof_examples:
        batch = label_data[j:j+batch_size]
    else:
        x1 = label_data[j:nrof_examples]
        x2 = label_data[0:nrof_examples-j]
        batch = np.vstack([x1,x2])
    batch_int = batch.astype(np.int64)
    return batch_int

def get_batch(image_data, batch_size, batch_index):
    nrof_examples = np.size(image_data, 0)
    j = batch_index*batch_size % nrof_examples
    if j+batch_size<=nrof_examples:
        batch = image_data[j:j+batch_size,:,:,:]
    else:
        x1 = image_data[j:nrof_examples,:,:,:]
        x2 = image_data[0:nrof_examples-j,:,:,:]
        batch = np.vstack([x1,x2])
    batch_float = batch.astype(np.float32)
    return batch_float

def get_triplet_batch(triplets, batch_index, batch_size):
    ax, px, nx = triplets
    a = get_batch(ax, int(batch_size/3), batch_index)
    p = get_batch(px, int(batch_size/3), batch_index)
    n = get_batch(nx, int(batch_size/3), batch_index)
    batch = np.vstack([a, p, n])
    return batch

def get_learning_rate_from_file(filename, epoch):
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.split('#', 1)[0]
            if line:
                par = line.strip().split(':')
                e = int(par[0])
                lr = float(par[1])
                if e <= epoch:
                    learning_rate = lr
                else:
                    return learning_rate

class ImageClass():
    "Stores the paths to images for a given class"
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths
  
    def __str__(self):
        return self.name + ', ' + str(len(self.image_paths)) + ' images'
  
    def __len__(self):
        return len(self.image_paths)
  
def get_dataset(path, has_class_directories=True):
    dataset = []
    path_exp = os.path.expanduser(path)
    classes = os.listdir(path_exp)
    classes.sort()
    nrof_classes = len(classes)
    for i in range(nrof_classes):
        class_name = classes[i]
        facedir = os.path.join(path_exp, class_name)
        image_paths = get_image_paths(facedir)
        dataset.append(ImageClass(class_name, image_paths))
  
    return dataset

def get_image_paths(facedir):
    image_paths = []
    if os.path.isdir(facedir):
        images = os.listdir(facedir)
        image_paths = [os.path.join(facedir,img) for img in images]
    return image_paths
  
def split_dataset(dataset, split_ratio, mode):
    if mode=='SPLIT_CLASSES':
        nrof_classes = len(dataset)
        class_indices = np.arange(nrof_classes)
        np.random.shuffle(class_indices)
        split = int(round(nrof_classes*split_ratio))
        train_set = [dataset[i] for i in class_indices[0:split]]
        test_set = [dataset[i] for i in class_indices[split:-1]]
    elif mode=='SPLIT_IMAGES':
        train_set = []
        test_set = []
        min_nrof_images = 2
        for cls in dataset:
            paths = cls.image_paths
            np.random.shuffle(paths)
            split = int(round(len(paths)*split_ratio))
            if split<min_nrof_images:
                continue  # Not enough images for test set. Skip class...
            train_set.append(ImageClass(cls.name, paths[0:split]))
            test_set.append(ImageClass(cls.name, paths[split:-1]))
    else:
        raise ValueError('Invalid train/test split mode "%s"' % mode)
    return train_set, test_set


def load_model(model):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)

        saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))

def load_model_LCNN29(model_path, saver):
	# saver = tf.train.Saver()
	saver.restore(tf.get_default_session(), model_path)


def load_model_collection(model,fix_variables):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)


        # saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))

        saver = tf.train.Saver(fix_variables)
        saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))

def load_model_softmax(model):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)

        # saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        all_varibales = tf.trainable_variables()
        all_varibales = all_varibales[:-2]
        saver = tf.train.Saver(all_varibales)
        saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))



def load_DPMISNs_model_softmax(model):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)

        # saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        all_varibales = tf.trainable_variables()
        all_varibales = all_varibales[:-4]
        print('para withou load:')
        print(all_varibales[-4])
        print(all_varibales[-3])
        print(all_varibales[-2])
        print(all_varibales[-1])
        saver = tf.train.Saver(all_varibales)
        saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))

def load_model_JBloss(model):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp,'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)
        
        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)
      
        # saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        all_varibales = tf.trainable_variables()
        all_varibales = all_varibales[:-2]
        saver = tf.train.Saver(all_varibales)
        saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))


def load_model_JBloss_ABG(model):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)

        # saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        all_varibales = tf.trainable_variables()
        all_varibales = all_varibales[:-3]
        saver = tf.train.Saver(all_varibales)
        saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))

def load_model_mine(model):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)
        sess_FaceNet2 = tf.Session()
        saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        saver.restore(sess_FaceNet2, os.path.join(model_exp, ckpt_file))

        # Get input and output tensors
        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

        # with tf.Graph().as_default():
        #     with tf.Session() as sess_FaceNet2:
        #         saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        #         saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))
        #
        #         # Get input and output tensors
        #         images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        #         embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        #         phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

        # FaceNet = tf.Graph()
        # sess_FaceNet2 = tf.Session(graph=FaceNet)
        # with FaceNet.as_default():
        #     saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        #     saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))
        #
        # sess_FaceNet2 = tf.Session()

        # Get input and output tensors
        # images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        # embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        # phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        return sess_FaceNet2,images_placeholder,embeddings,phase_train_placeholder

def load_model_mineGPU(model,gpu_memory_fraction):
    # Check if the model is a model directory (containing a metagraph and a checkpoint file)
    #  or if it is a protobuf file with a frozen graph
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = get_model_filenames(model_exp)

        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        
        sess_FaceNet2 = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file))
        saver.restore(sess_FaceNet2, os.path.join(model_exp, ckpt_file))

        # Get input and output tensors
        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

        return sess_FaceNet2,images_placeholder,embeddings,phase_train_placeholder

def get_model_filenames(model_dir):
    files = os.listdir(model_dir)
    meta_files = [s for s in files if s.endswith('.meta')]
    if len(meta_files)==0:
        raise ValueError('No meta file found in the model directory (%s)' % model_dir)
    elif len(meta_files)>1:
        raise ValueError('There should not be more than one meta file in the model directory (%s)' % model_dir)
    meta_file = meta_files[0]
    meta_files = [s for s in files if '.ckpt' in s]
    max_step = -1
    for f in files:
        step_str = re.match(r'(^model-[\w\- ]+.ckpt-(\d+))', f)
        if step_str is not None and len(step_str.groups())>=2:
            step = int(step_str.groups()[1])
            if step > max_step:
                max_step = step
                ckpt_file = step_str.groups()[0]
    return meta_file, ckpt_file


def distance(embeddings1, embeddings2, distance_metric=0):
    if distance_metric == 0:
        # Euclidian distance
        diff = np.subtract(embeddings1, embeddings2)
        dist = np.sum(np.square(diff), 1)
    elif distance_metric == 1:
        # Distance based on cosine similarity
        dot = np.sum(np.multiply(embeddings1, embeddings2), axis=1)
        norm = np.linalg.norm(embeddings1, axis=1) * np.linalg.norm(embeddings2, axis=1)
        similarity = dot / norm
        dist = np.arccos(similarity) / math.pi
    else:
        raise 'Undefined distance metric %d' % distance_metric

    return dist
def calculate_roc(thresholds, embeddings1, embeddings2, actual_issame, nrof_folds=10):
    assert(embeddings1.shape[0] == embeddings2.shape[0])
    assert(embeddings1.shape[1] == embeddings2.shape[1])
    nrof_pairs = min(len(actual_issame), embeddings1.shape[0])
    nrof_thresholds = len(thresholds)
    k_fold = KFold(n_splits=nrof_folds, shuffle=False)
    
    tprs = np.zeros((nrof_folds,nrof_thresholds))
    fprs = np.zeros((nrof_folds,nrof_thresholds))
    accuracy = np.zeros((nrof_folds))
    
    diff = np.subtract(embeddings1, embeddings2)
    dist = np.sum(np.square(diff),1)
    indices = np.arange(nrof_pairs)
    
    for fold_idx, (train_set, test_set) in enumerate(k_fold.split(indices)):
        
        # Find the best threshold for the fold
        acc_train = np.zeros((nrof_thresholds))
        for threshold_idx, threshold in enumerate(thresholds):
            _, _, acc_train[threshold_idx] = calculate_accuracy(threshold, dist[train_set], actual_issame[train_set])
        best_threshold_index = np.argmax(acc_train)
        for threshold_idx, threshold in enumerate(thresholds):
            tprs[fold_idx,threshold_idx], fprs[fold_idx,threshold_idx], _ = calculate_accuracy(threshold, dist[test_set], actual_issame[test_set])
        _, _, accuracy[fold_idx] = calculate_accuracy(thresholds[best_threshold_index], dist[test_set], actual_issame[test_set])
          
    tpr = np.mean(tprs,0)
    fpr = np.mean(fprs,0)
    return tpr, fpr, accuracy


def calculate_roc_get_dist(thresholds, embeddings1, embeddings2, actual_issame, nrof_folds=10):
    assert (embeddings1.shape[0] == embeddings2.shape[0])
    assert (embeddings1.shape[1] == embeddings2.shape[1])
    nrof_pairs = min(len(actual_issame), embeddings1.shape[0])
    nrof_thresholds = len(thresholds)
    k_fold = KFold(n_splits=nrof_folds, shuffle=False)

    tprs = np.zeros((nrof_folds, nrof_thresholds))
    fprs = np.zeros((nrof_folds, nrof_thresholds))
    accuracy = np.zeros((nrof_folds))

    diff = np.subtract(embeddings1, embeddings2)
    dist = np.sum(np.square(diff), 1)
    indices = np.arange(nrof_pairs)
    import scipy.io as sio
    sio.savemat('./NewPaperTools/' + 'NIR_VIS_plot.mat', {'dist': dist, 'actual_issame': actual_issame})

    for fold_idx, (train_set, test_set) in enumerate(k_fold.split(indices)):

        # Find the best threshold for the fold
        acc_train = np.zeros((nrof_thresholds))
        for threshold_idx, threshold in enumerate(thresholds):
            _, _, acc_train[threshold_idx] = calculate_accuracy(threshold, dist[train_set], actual_issame[train_set])
        best_threshold_index = np.argmax(acc_train)
        for threshold_idx, threshold in enumerate(thresholds):
            tprs[fold_idx, threshold_idx], fprs[fold_idx, threshold_idx], _ = calculate_accuracy(threshold,
                                                                                                 dist[test_set],
                                                                                                 actual_issame[
                                                                                                     test_set])
        _, _, accuracy[fold_idx] = calculate_accuracy(thresholds[best_threshold_index], dist[test_set],
                                                      actual_issame[test_set])

    tpr = np.mean(tprs, 0)
    fpr = np.mean(fprs, 0)
    return tpr, fpr, accuracy

def calculate_accuracy(threshold, dist, actual_issame):
    predict_issame = np.less(dist, threshold)
    tp = np.sum(np.logical_and(predict_issame, actual_issame))
    fp = np.sum(np.logical_and(predict_issame, np.logical_not(actual_issame)))
    tn = np.sum(np.logical_and(np.logical_not(predict_issame), np.logical_not(actual_issame)))
    fn = np.sum(np.logical_and(np.logical_not(predict_issame), actual_issame))
  
    tpr = 0 if (tp+fn==0) else float(tp) / float(tp+fn)
    fpr = 0 if (fp+tn==0) else float(fp) / float(fp+tn)
    acc = float(tp+tn)/dist.size
    return tpr, fpr, acc


  
def calculate_val(thresholds, embeddings1, embeddings2, actual_issame, far_target, nrof_folds=10):
    assert(embeddings1.shape[0] == embeddings2.shape[0])
    assert(embeddings1.shape[1] == embeddings2.shape[1])
    nrof_pairs = min(len(actual_issame), embeddings1.shape[0])
    nrof_thresholds = len(thresholds)
    k_fold = KFold(n_splits=nrof_folds, shuffle=False)
    
    val = np.zeros(nrof_folds)
    far = np.zeros(nrof_folds)
    
    diff = np.subtract(embeddings1, embeddings2)
    dist = np.sum(np.square(diff),1)
    indices = np.arange(nrof_pairs)
    
    for fold_idx, (train_set, test_set) in enumerate(k_fold.split(indices)):
      
        # Find the threshold that gives FAR = far_target
        far_train = np.zeros(nrof_thresholds)
        for threshold_idx, threshold in enumerate(thresholds):
            _, far_train[threshold_idx] = calculate_val_far(threshold, dist[train_set], actual_issame[train_set])
        if np.max(far_train)>=far_target:
            f = interpolate.interp1d(far_train, thresholds, kind='slinear')
            threshold = f(far_target)
        else:
            threshold = 0.0
    
        val[fold_idx], far[fold_idx] = calculate_val_far(threshold, dist[test_set], actual_issame[test_set])
  
    val_mean = np.mean(val)
    far_mean = np.mean(far)
    val_std = np.std(val)
    return val_mean, val_std, far_mean



def calculate_val_far(threshold, dist, actual_issame):
    predict_issame = np.less(dist, threshold)
    true_accept = np.sum(np.logical_and(predict_issame, actual_issame))
    false_accept = np.sum(np.logical_and(predict_issame, np.logical_not(actual_issame)))
    n_same = np.sum(actual_issame)
    n_diff = np.sum(np.logical_not(actual_issame))
    val = float(true_accept) / float(n_same)
    far = float(false_accept) / float(n_diff)
    return val, far

def store_revision_info(src_path, output_dir, arg_string):
    try:
        # Get git hash
        cmd = ['git', 'rev-parse', 'HEAD']
        gitproc = Popen(cmd, stdout = PIPE, cwd=src_path)
        (stdout, _) = gitproc.communicate()
        git_hash = stdout.strip()
    except OSError as e:
        git_hash = ' '.join(cmd) + ': ' +  e.strerror
  
    try:
        # Get local changes
        cmd = ['git', 'diff', 'HEAD']
        gitproc = Popen(cmd, stdout = PIPE, cwd=src_path)
        (stdout, _) = gitproc.communicate()
        git_diff = stdout.strip()
    except OSError as e:
        git_diff = ' '.join(cmd) + ': ' +  e.strerror
    
    # Store a text file in the log directory
    rev_info_filename = os.path.join(output_dir, 'revision_info.txt')
    with open(rev_info_filename, "w") as text_file:
        text_file.write('arguments: %s\n--------------------\n' % arg_string)
        text_file.write('tensorflow version: %s\n--------------------\n' % tf.__version__)  # @UndefinedVariable
        text_file.write('git hash: %s\n--------------------\n' % git_hash)
        text_file.write('%s' % git_diff)

def list_variables(filename):
    reader = training.NewCheckpointReader(filename)
    variable_map = reader.get_variable_to_shape_map()
    names = sorted(variable_map.keys())
    return names

def put_images_on_grid(images, shape=(16,8)):
    nrof_images = images.shape[0]
    img_size = images.shape[1]
    bw = 3
    img = np.zeros((shape[1]*(img_size+bw)+bw, shape[0]*(img_size+bw)+bw, 3), np.float32)
    for i in range(shape[1]):
        x_start = i*(img_size+bw)+bw
        for j in range(shape[0]):
            img_index = i*shape[0]+j
            if img_index>=nrof_images:
                break
            y_start = j*(img_size+bw)+bw
            img[x_start:x_start+img_size, y_start:y_start+img_size, :] = images[img_index, :, :, :]
        if img_index>=nrof_images:
            break
    return img

def write_arguments_to_file(args, filename):
    with open(filename, 'w') as f:
        for key, value in iteritems(vars(args)):
            f.write('%s: %s\n' % (key, str(value)))