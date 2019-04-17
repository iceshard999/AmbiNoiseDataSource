
# coding: utf-8

# In[1]:


import os
import pandas as pd
from obspy import read, Trace
from obspy.core import stream
from obspy.core import UTCDateTime


# In[18]:


from tqdm import tqdm
class AmbiNoiseDataSource:
    def __init__(self, rootPath, stationFile='', respFile=''):
        self.root = rootPath
        self.staList = self.GetStaListFrom(stationFile)
        self.respList = self.GetRespListFrom(respFile)
        self.dataList = []
        #self.dataSheet = pd.DataFrame(columns=('StaName','Year','jDay','Path'))
#        if os.path.exists(rootPath) and os.path.isdir(rootPath):
#            self.makeDataSheet()
    def GetStaListFrom(self,file):
        l = []
        return l
    def GetRespListFrom(self,file):
        l = []
        return l
    def checkFile(self, filename):
        try:
            s = read(filename)
        except:
            return False
        else:
            #print(s[0].stats)
            for tr in s:
                if tr.stats.delta > 0 and tr.stats.npts > 0:
                    return True
            return False
    def addPathToList(self,sta,year,jday,channel,path):
        for line in self.dataList:
            if line['staName'] == sta and line['year'] == year and line['jday'] == jday and line['channel'] == channel:
                if path in line['path']:
                    return
                else:
                    line['path'].append(path)
                    return
        newline = {'staName':sta, 'year':year, 'jday':jday, 'channel':channel, 'path':[path]}
        self.dataList.append(newline)
    def makeDataSheet(self):
        if os.path.exists(self.root)==False or os.path.isdir(self.root)==False:
            return
        for (root,dirs,files) in os.walk(self.root):
            print('entering directory: '+root)
            for fn in tqdm(files):
                #print(os.path.join(root,fn))
                fullpath = os.path.join(root,fn)
                if self.checkFile(fullpath):
                    s = read(fullpath)
                    for tr in s:
                        sta = tr.stats.station
                        net = tr.stats.network
                        bTime = tr.stats.starttime
                        eTime = tr.stats.endtime
                        channel = tr.stats.channel[-1]
                        if bTime.year == eTime.year:
                            if bTime.julday == eTime.julday:
                                self.addPathToList(sta,bTime.year,bTime.julday,channel,fullpath)
                            else:
                                for jday in range(bTime.julday,eTime.julday+1):
                                    self.addPathToList(sta,bTime.year,jday,channel,fullpath)
                        else:
                            for yr in range(bTime.year,eTime.year+1):
                                if yr < eTime.year:
                                    for jday in range(bTime.julday,366):
                                        self.addPathToList(sta,yr,jday,channel,fullpath)
                                else:
                                    for jday in range(1,eTime.julday+1):
                                        self.addPathToList(sta,yr,jday,channel,fullpath)
    def DataFrame(self):
        data = pd.DataFrame(self.dataList)
        data=data[['staName','channel','year','jday','path']]
        return data
    def toCSV(self,path):
        data = self.DataFrame()
        data.to_csv(path)
    def fromCSV(self,path):
        df = pd.read_csv(path)
        self.dataList = []
        func = lambda x,y:x if y in x else x + [y]
        for i in tqdm(range(0,df.shape[0])):
            sta = df.loc[i,'staName']
            yr = df.loc[i,'year']
            jday = df.loc[i,'jday']
            channel = df.loc[i,'channel']
            files = df.loc[i,'path']
            filelist = []
            for f in files.split(','):
                f = f.replace('"','')
                f = f.replace('\'','')
                f = f.replace(' ','')
                f = f.replace('[','')
                f = f.replace(']','')
                if f not in filelist:
                    filelist.append(f)
            newline = {'staName':sta, 'year':yr, 'jday':jday, 'channel':channel, 'path':filelist}
            self.dataList.append(newline)
    def output(self,desPath,components=['Z'],sampleRate=5.0,lowpass=True,freq=0.5):
        for line in tqdm(self.dataList):
            staName,channel,year,jday,paths = line['staName'],line['channel'],line['year'],line['jday'],line['path']
            if channel in components:
                outDir = "%s/%s/%d" %(desPath,staName,year)
                outPath = "%s/%s_%s_%03d.sac" %(outDir,staName,channel,jday)       
                #print(outPath)
                if os.path.exists(outDir) == False:
                    os.makedirs(outDir)
                formattedSAC = self.reFormatSAC(paths,year,jday,newRate=sampleRate,channel=channel)
                if formattedSAC.count > 0:
                    if lowpass == True:
                        formattedSAC.filter("lowpass",freq=freq)
                    formattedSAC.write(outPath)
    def reFormatSAC(self,paths,year,jday,newRate=5.0,channel='Z'):
        newSAC = stream.Stream()
        try:
            oldSAC = read(paths)
        except:
            oldSAC = stream.Stream()
            for nm in paths:
                try:
                    aSAC = read(nm)
                except:
                    print('Error reading '+nm)
                else:
                    for tr in aSAC:
                        if channel in tr.stats.channel:
                            oldSAC.append(tr)
        for tr in oldSAC:
            oldRate = tr.stats.sampling_rate
            mul = int(oldRate/newRate)
            if mul > 0:
                tr.decimate(mul,strict_length=False,no_filter=True)
                tr.stats.sampling_rate = newRate
                newSAC.append(tr)    
        if newSAC.count() > 0:
            newSAC.merge(method=0,fill_value="interpolate")
            newSAC.detrend()
            tB = UTCDateTime(year=year, julday=jday, hour=0, minute=0, second=0, microsecond=0)
            tE = tB + 3600*24
            new=newSAC.trim(starttime=tB, endtime=tE, pad=True, fill_value=0, nearest_sample=False)
            return new
        else:
            return newSAC
                

if __name__ == "__main__":
    ds = AmbiNoiseDataSource('/Volumes/RFDATA/CAGS-40')
    ds.makeDataSheet()
    ds.toCSV('./process.csv')
    ds.output('/Volumes/Seagate Backup Plus Drive/CAS-converted')
'''
    OR:
    ds.output('/Volumes/Seagate Backup Plus Drive/CAS-converted',
        component=['E','N','Z'],
        sampleRate=5.0,
        lowpass=True,freq=0.5)
'''
