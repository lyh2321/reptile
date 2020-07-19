


with open("/Users/lyh/Downloads/kk/courseschedule0.js", "r") as f:
    var = f.readlines()
    num = 0
    varlen = len(var)
    for i in range(0,varlen):
        print(var[i])
        if(i >= varlen/7*num):
            num=num+1
        with open('/Users/lyh/Downloads/kk/courseschedulesss'+str(num)+'.js', 'a+') as fn:
            fn.write(var[i] + '\n')